#!/usr/bin/env node
// Push this repo's NATIVE finished posts to the Wildlife Dominion dashboard.
//
// This does NOT change the local content format. It reads content/posts/*.json
// (the same files the WordPress publisher consumes) and forwards a mapped payload
// to the dashboard ingest API. The dashboard is the single approval gate: every
// post is pushed as status `in_review` and must be Approved there before it is
// published to WordPress/Shopify.
//
// externalId is the PERMANENT identity (a stable calendar/article id such as
// jul26_01), set once in the post and never changed. The slug is a separate SEO
// field that may change freely (e.g. "ranchers" -> "landowners") without orphaning
// the dashboard entry. externalId must NEVER be derived from the slug.
//
// Push the CURRENT batch only — never the whole folder by default (it may hold
// back-catalog / already-published posts). A bare invocation is refused.
//
// Usage:
//   node scripts/push-content.mjs content/posts/jul26_*.json --period 2026-07  # explicit batch
//   node scripts/push-content.mjs --period 2026-07                             # scope folder to one cycle
//   node scripts/push-content.mjs content/posts/jul26_01_wp_draft.json --period 2026-07
//   node scripts/push-content.mjs <paths...> --author-email you@example.com
//   node scripts/push-content.mjs <paths...> --period 2026-07 --dry-run
//
// Required env (from gitignored .env locally, or CI/repo secrets — never commit the key):
//   DASHBOARD_URL   e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev
//   WD_INGEST_KEY   secret ingest key
// Optional env:
//   WD_AUTHOR_EMAIL default authorEmail when --author-email is not passed
import 'dotenv/config';
import { execFile } from 'node:child_process';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const BRAND = 'hogeye-cameras';
const REPO_ROOT = fileURLToPath(new URL('..', import.meta.url));
const DEFAULT_DIR = path.join(REPO_ROOT, 'content', 'posts');
const execFileAsync = promisify(execFile);

function fail(message) {
  console.error(`\n[push:content] ${message}\n`);
  process.exit(1);
}

function parseDashboardResponse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function formatReason(reason) {
  if (typeof reason === 'string') return reason;
  try {
    return JSON.stringify(reason);
  } catch {
    return String(reason);
  }
}

function printReasons(reasons, output = console.error) {
  if (!Array.isArray(reasons) || reasons.length === 0) {
    output('[push:content] reasons: []');
    return;
  }
  reasons.forEach((reason, index) => {
    output(`[push:content] reason[${index + 1}]: ${formatReason(reason)}`);
  });
}

// --- CLI args -------------------------------------------------------------
const argv = process.argv.slice(2);
const inputs = [];
let cliPeriod = null;
let cliAuthorEmail = null;
let cliDryRun = false;
for (let i = 0; i < argv.length; i += 1) {
  const a = argv[i];
  if (a === '--period') {
    cliPeriod = argv[++i];
  } else if (a.startsWith('--period=')) {
    cliPeriod = a.slice('--period='.length);
  } else if (a === '--author-email') {
    cliAuthorEmail = argv[++i];
  } else if (a.startsWith('--author-email=')) {
    cliAuthorEmail = a.slice('--author-email='.length);
  } else if (a === '--dry-run') {
    cliDryRun = true;
  } else if (a.startsWith('--')) {
    fail(`Unknown flag: ${a}`);
  } else {
    inputs.push(a);
  }
}

const { DASHBOARD_URL, WD_INGEST_KEY, WD_AUTHOR_EMAIL } = process.env;
if (!DASHBOARD_URL && !cliDryRun) {
  fail('Missing DASHBOARD_URL. Set it in a gitignored .env or CI secret (e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev).');
}
if (!WD_INGEST_KEY && !cliDryRun) {
  fail('Missing WD_INGEST_KEY. Set it in a gitignored .env or CI secret — never commit this value.');
}
const authorEmail = cliAuthorEmail || WD_AUTHOR_EMAIL || null;

// --- helpers --------------------------------------------------------------
const MONTHS = {
  jan: '01', feb: '02', mar: '03', apr: '04', may: '05', jun: '06',
  jul: '07', aug: '08', sep: '09', oct: '10', nov: '11', dec: '12',
};

// The file's own YYYY-MM, ignoring any --period override. Priority: a period/month
// field, an ISO `date` field, or the filename prefix (e.g. may26_01... -> 2026-05).
// Used both as a fallback and to FILTER which files belong to the requested cycle.
function nativePeriod(item, filePath) {
  const fromField = item.period || item.month;
  if (typeof fromField === 'string' && /^\d{4}-\d{2}$/.test(fromField.trim())) {
    return fromField.trim();
  }
  if (typeof item.date === 'string' && /^\d{4}-\d{2}/.test(item.date)) {
    return item.date.slice(0, 7);
  }
  const base = path.basename(filePath).toLowerCase();
  const m = base.match(/^([a-z]{3})(\d{2})/);
  if (m && MONTHS[m[1]]) {
    return `20${m[2]}-${MONTHS[m[1]]}`;
  }
  return null;
}

// Publication month sent to the dashboard: explicit --period wins, else the file's own.
function derivePeriod(item, filePath) {
  return cliPeriod || nativePeriod(item, filePath);
}

// Resolve the body string whether `content` is a flat string or a nested object.
function resolveBody(raw) {
  if (typeof raw === 'string') return raw;
  if (raw && typeof raw === 'object') {
    return raw.md || raw.markdown || raw.html || raw.raw || raw.rendered || '';
  }
  return '';
}

// A post's STABLE dashboard identity. This must NOT be the slug: the slug is an
// SEO field that can change, and keying on it would orphan the old entry and create
// a duplicate. Use a permanent id (externalId / article_id / calendar id) that is
// set once and never changed.
function stableExternalId(item, nested) {
  const candidate =
    item.externalId ?? item.external_id ?? item.article_id ?? item.articleId ?? item.id ??
    nested.externalId ?? nested.external_id ?? nested.article_id ?? nested.articleId ?? nested.id;
  if (typeof candidate === 'number') return String(candidate);
  if (typeof candidate === 'string' && candidate.trim()) return candidate.trim();
  return null;
}

function versionFields(item, nested) {
  return {
    versionOfExternalId:
      item.versionOfExternalId ??
      item.version_of_external_id ??
      nested.versionOfExternalId ??
      nested.version_of_external_id ??
      null,
    createVersion: item.createVersion ?? nested.createVersion ?? null,
    version: item.version ?? nested.version ?? null,
  };
}

// Map a loaded item to the dashboard payload. Supports the flat shape and a
// nested brief/content shape without changing the on-disk format.
// Returns { payload } on success or { skip: reason } when the post can't be pushed.
function mapItem(rawItem, filePath) {
  // Flatten a possible wrapper object (brief/post/data) while letting top-level win.
  const nested = (rawItem.brief || rawItem.post || rawItem.data || {});
  const item = { ...nested, ...rawItem };

  const title = item.title ?? nested.title;
  const slug = item.slug ?? nested.slug;
  const body = resolveBody(item.content ?? nested.content);
  const targetKeyword =
    item.focus_keyword ?? item.targetKeyword ?? nested.focus_keyword ?? nested.targetKeyword ?? null;
  const externalId = stableExternalId(item, nested);

  if (!title || !slug) return { skip: 'missing title/slug' };
  if (!externalId) {
    return {
      skip:
        'missing stable externalId — add a permanent "externalId" (e.g. the article/calendar id ' +
        'like jul26_01) to the post JSON. Never use the slug as identity: it can change.',
    };
  }

  const versions = versionFields(item, nested);
  const hasVersionFields =
    String(externalId).endsWith("-v2") ||
    versions.versionOfExternalId != null ||
    versions.createVersion != null ||
    versions.version != null;
  if (hasVersionFields) {
    if (
      typeof versions.versionOfExternalId !== 'string' ||
      !versions.versionOfExternalId.trim()
    ) {
      return { skip: 'V2 content requires versionOfExternalId' };
    }
    if (versions.createVersion !== true) {
      return { skip: 'V2 content requires createVersion=true' };
    }
    if (versions.version !== 2) {
      return { skip: 'V2 content requires version=2' };
    }
  }

  const payload = {
    brand: BRAND,
    externalId,
    title,
    slug,
    bodyMd: body,
    targetKeyword,
    period: derivePeriod(item, filePath),
    status: 'in_review',
  };
  if (hasVersionFields) {
    payload.versionOfExternalId = versions.versionOfExternalId.trim();
    payload.createVersion = true;
    payload.version = versions.version;
  }
  if (authorEmail) payload.authorEmail = authorEmail;
  return { payload };
}

async function runQualityPreflight(files) {
  const script = path.join(REPO_ROOT, 'scripts', 'seo', 'hogeye_content_quality.py');
  let python = process.env.PYTHON || path.join(REPO_ROOT, '.venv', 'bin', 'python');
  try {
    await stat(python);
  } catch {
    python = process.env.PYTHON || 'python3';
  }

  let result;
  try {
    result = await execFileAsync(python, [script, '--json', ...files], {
      cwd: REPO_ROOT,
      maxBuffer: 1024 * 1024,
    });
  } catch (error) {
    const detail = error?.stdout || error?.stderr || error?.message || error;
    fail(`HogEye content-quality preflight failed:\n${detail}`);
  }

  let report;
  try {
    report = JSON.parse(result.stdout);
  } catch {
    fail(`HogEye content-quality preflight returned invalid JSON:\n${result.stdout}`);
  }
  if (!report.ok) {
    const failures = report.reports
      .filter((entry) => !entry.ok)
      .map((entry) => `${entry.path}: ${entry.errors.join('; ')}`)
      .join('\n');
    fail(`HogEye content-quality preflight failed:\n${failures}`);
  }
  for (const entry of report.reports) {
    console.log(
      `[push:content] quality PASS ${path.basename(entry.path)} ` +
        `words=${entry.wordCount} target=${entry.targetWordCount}`,
    );
  }
}

async function runEditorialPreflight(files) {
  const script = path.join(REPO_ROOT, 'scripts', 'editorial-gate.mjs');
  const baseline = path.join(
    REPO_ROOT,
    'workspace',
    'brand_truth',
    'BRAND_BASELINE.md',
  );
  try {
    await execFileAsync(
      process.execPath,
      [script, '--baseline', baseline, ...files],
      {
        cwd: REPO_ROOT,
        env: process.env,
        maxBuffer: 4 * 1024 * 1024,
      },
    );
  } catch (error) {
    const detail = error?.stdout || error?.stderr || error?.message || error;
    fail(`HogEye editorial style/taste gate failed:\n${detail}`);
  }
}

// Guard: never bulk-push the whole content/posts folder by accident (it may hold
// back-catalog / already-published posts). Require explicit file paths, or a
// --period that scopes the default folder to just that cycle's files.
async function collectFiles(args) {
  if (!args.length && !cliPeriod) {
    fail(
      'Refusing to push the entire content/posts/ folder (it may contain back-catalog or\n' +
      'already-published posts). Push the CURRENT batch only — pass explicit file paths, e.g.\n' +
      '  npm run push:content -- content/posts/jul26_*.json --period 2026-07\n' +
      'or scope the default folder to one cycle with --period, e.g.\n' +
      '  npm run push:content -- --period 2026-07',
    );
  }
  const targets = args.length ? args : [DEFAULT_DIR];
  const files = [];
  for (const t of targets) {
    const abs = path.isAbsolute(t) ? t : path.join(process.cwd(), t);
    let st;
    try {
      st = await stat(abs);
    } catch {
      fail(`Path not found: ${t}`);
    }
    if (st.isDirectory()) {
      const entries = await readdir(abs);
      for (const name of entries.sort()) {
        if (!name.endsWith('.json')) continue;
        if (name.toLowerCase().includes('example')) continue;
        files.push(path.join(abs, name));
      }
    } else {
      files.push(abs);
    }
  }
  return files;
}

// --- main -----------------------------------------------------------------
const endpoint = DASHBOARD_URL ? `${DASHBOARD_URL.replace(/\/+$/, '')}/api/ingest` : null;
const files = await collectFiles(inputs);
if (!files.length) {
  fail('No content JSON files found to push.');
}

// When scanning the default folder with --period, only push files that belong to
// that cycle. Explicit file paths are pushed as given (no period filter).
const periodFilterMode = inputs.length === 0 && Boolean(cliPeriod);
const qualityFiles = [];
for (const file of files) {
  if (!periodFilterMode) {
    qualityFiles.push(file);
    continue;
  }
  try {
    const item = JSON.parse(await readFile(file, 'utf8'));
    if (nativePeriod(item, file) === cliPeriod) qualityFiles.push(file);
  } catch {
    // Keep invalid JSON in the quality batch so the preflight reports it.
    qualityFiles.push(file);
  }
}
if (!qualityFiles.length) {
  fail(`No content JSON files found in cycle ${cliPeriod}.`);
}
await runQualityPreflight(qualityFiles);
await runEditorialPreflight(qualityFiles);

let pushed = 0;
let skipped = 0;
let failures = 0;

for (const file of files) {
  let item;
  try {
    item = JSON.parse(await readFile(file, 'utf8'));
  } catch (err) {
    console.error(`[push:content] SKIP ${path.basename(file)} — invalid JSON: ${err?.message ?? err}`);
    failures += 1;
    continue;
  }

  if (periodFilterMode && nativePeriod(item, file) !== cliPeriod) {
    console.warn(`[push:content] SKIP ${path.basename(file)} — not in cycle ${cliPeriod}`);
    skipped += 1;
    continue;
  }

  const mapped = mapItem(item, file);
  if (mapped.skip) {
    console.warn(`[push:content] SKIP ${path.basename(file)} — ${mapped.skip}`);
    skipped += 1;
    continue;
  }
  const { payload } = mapped;

  if (cliDryRun) {
    console.log(`[push:content] DRY RUN ${JSON.stringify(payload)}`);
    pushed += 1;
    continue;
  }

  let res;
  try {
    res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'x-ingest-key': WD_INGEST_KEY,
        'content-type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.error(`[push:content] FAIL ${payload.slug} — network error: ${err?.message ?? err}`);
    failures += 1;
    continue;
  }

  const text = await res.text();
  const responseBody = parseDashboardResponse(text);
  console.log(`[push:content] POST ${endpoint} (id=${payload.externalId} slug=${payload.slug}) -> ${res.status} ${res.statusText}`);
  if (res.status === 200) {
    console.log(`[push:content] quality=${responseBody?.quality ?? 'unknown'}`);
    if (Array.isArray(responseBody?.reasons) && responseBody.reasons.length > 0) {
      printReasons(responseBody.reasons, console.log);
    }
  }
  if (!res.ok) {
    const classification =
      res.status === 422
        ? 'content failure'
        : res.status === 503
          ? 'retryable'
          : 'request failure';
    console.error(`[push:content] ${classification} status=${res.status}`);
    console.error(`[push:content] error: ${responseBody?.error ?? responseBody?.raw ?? '(none)'}`);
    printReasons(responseBody?.reasons);
    failures += 1;
    continue;
  }
  pushed += 1;
}

console.log(
  `\n[push:content] brand="${BRAND}" pushed=${pushed} skipped=${skipped} failed=${failures} ` +
    `(${cliDryRun ? 'dry-run' : 'status=in_review'})`,
);

if (failures > 0) {
  process.exit(1);
}
