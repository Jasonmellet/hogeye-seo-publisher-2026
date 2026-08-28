#!/usr/bin/env node
// Pull this brand's dashboard-approved content.
//
// Default: list approved items (ready for the publish pipeline — NOT live).
// --check / --apply: sync Schell/reviewer hub edits into local content/posts/*.json
// by stable externalId. Hub is source of truth for approved posts until publish.
//
// After --apply, publish from the updated local files. Do NOT re-push to
// /api/ingest (that resets status to in_review).
// This script never publishes to WordPress/Shopify.
//
// Usage:
//   node scripts/pull-approved.mjs
//   node scripts/pull-approved.mjs --period 2026-07
//   node scripts/pull-approved.mjs --check
//   node scripts/pull-approved.mjs --apply --period 2026-07
//   node scripts/pull-approved.mjs --brand=hogeye-cameras --json
//   node scripts/pull-approved.mjs --out approved.json --fail-if-none
//
// Required env (gitignored .env locally, or CI/repo secrets — never commit the key):
//   DASHBOARD_URL   e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev
//   WD_INGEST_KEY   secret ingest key
// Optional env:
//   WD_BRAND        repo slug (boar-blanket | big-pig-traps | hogeye-cameras); defaults to this repo
import 'dotenv/config';
import { readFile, writeFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const DEFAULT_BRAND = 'hogeye-cameras';
const VALID_BRANDS = new Set(['boar-blanket', 'big-pig-traps', 'hogeye-cameras']);
const REPO_ROOT = fileURLToPath(new URL('..', import.meta.url));
const POSTS_DIR = path.join(REPO_ROOT, 'content', 'posts');

marked.setOptions({ gfm: true, breaks: true });

function fail(message) {
  console.error(`\n[pull:approved] ${message}\n`);
  process.exit(1);
}

// --- CLI args -------------------------------------------------------------
const argv = process.argv.slice(2);
let cliBrand = null;
let cliPeriod = null;
let outPath = null;
let asJson = false;
let failIfNone = false;
let doCheck = false;
let doApply = false;

for (let i = 0; i < argv.length; i += 1) {
  const a = argv[i];
  if (a === '--brand') {
    cliBrand = argv[++i];
  } else if (a.startsWith('--brand=')) {
    cliBrand = a.slice('--brand='.length);
  } else if (a === '--period') {
    cliPeriod = argv[++i];
  } else if (a.startsWith('--period=')) {
    cliPeriod = a.slice('--period='.length);
  } else if (a === '--out') {
    outPath = argv[++i];
  } else if (a.startsWith('--out=')) {
    outPath = a.slice('--out='.length);
  } else if (a === '--json') {
    asJson = true;
  } else if (a === '--fail-if-none') {
    failIfNone = true;
  } else if (a === '--check') {
    doCheck = true;
  } else if (a === '--apply') {
    doApply = true;
  } else if (a.startsWith('--')) {
    fail(`Unknown flag: ${a}`);
  } else {
    fail(`Unexpected argument: ${a}`);
  }
}

if (doCheck && doApply) {
  fail('Use either --check or --apply, not both.');
}

const { DASHBOARD_URL, WD_INGEST_KEY, WD_BRAND } = process.env;
if (!DASHBOARD_URL) {
  fail('Missing DASHBOARD_URL. Set it in a gitignored .env or CI secret (e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev).');
}
if (!WD_INGEST_KEY) {
  fail('Missing WD_INGEST_KEY. Set it in a gitignored .env or CI secret — never commit this value.');
}

const brand = (cliBrand || WD_BRAND || DEFAULT_BRAND).trim();
if (!VALID_BRANDS.has(brand)) {
  fail(`Invalid brand "${brand}". Expected one of: ${[...VALID_BRANDS].join(' | ')}.`);
}
if (cliPeriod && !/^\d{4}-\d{2}$/.test(cliPeriod)) {
  fail(`Invalid --period "${cliPeriod}". Expected YYYY-MM.`);
}

// --- helpers --------------------------------------------------------------
function asItems(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object') {
    for (const key of ['items', 'content', 'data', 'results']) {
      if (Array.isArray(payload[key])) return payload[key];
    }
  }
  return null;
}

function norm(value) {
  if (value == null) return '';
  return String(value).replace(/\r\n/g, '\n').trimEnd();
}

function isProbablyHtml(s) {
  return /<\/?(?:p|h[1-6]|ul|ol|li|div|br|a|strong|em|blockquote|table|tr|td|th)\b/i.test(s);
}

/** Map hub bodyMd into the local `content` field (HTML for the WP publisher). */
function hubBodyToLocalContent(bodyMd) {
  const raw = norm(bodyMd);
  if (!raw) return '';
  if (isProbablyHtml(raw)) return raw;
  return norm(marked.parse(raw, { async: false }));
}

function stableExternalId(item) {
  const nested = item?.brief || item?.post || item?.data || {};
  const candidate =
    item.externalId ?? item.external_id ?? item.article_id ?? item.articleId ?? item.id ??
    nested.externalId ?? nested.external_id ?? nested.article_id ?? nested.articleId ?? nested.id;
  if (typeof candidate === 'number') return String(candidate);
  if (typeof candidate === 'string' && candidate.trim()) return candidate.trim();
  return null;
}

function localFields(item) {
  const nested = item?.brief || item?.post || item?.data || {};
  const merged = { ...nested, ...item };
  const content = merged.content;
  const body =
    typeof content === 'string'
      ? content
      : content && typeof content === 'object'
        ? content.html || content.md || content.markdown || content.raw || content.rendered || ''
        : '';
  return {
    title: merged.title ?? null,
    slug: merged.slug ?? null,
    content: typeof body === 'string' ? body : '',
    focus_keyword: merged.focus_keyword ?? merged.targetKeyword ?? null,
  };
}

function hubFields(hub) {
  const kw = hub.targetKeyword ?? hub.focus_keyword;
  return {
    externalId: stableExternalId(hub),
    title: hub.title ?? null,
    slug: hub.slug ?? null,
    content: hubBodyToLocalContent(hub.bodyMd ?? ''),
    focus_keyword: kw == null || kw === '' ? null : String(kw),
    period: hub.period ?? hub.month ?? null,
  };
}

function fieldDiffs(local, hub) {
  const diffs = [];
  for (const key of ['title', 'slug', 'content', 'focus_keyword']) {
    // Only sync focus_keyword when the hub sent one.
    if (key === 'focus_keyword' && hub.focus_keyword == null) continue;
    if (norm(local[key]) !== norm(hub[key])) diffs.push(key);
  }
  return diffs;
}

async function indexLocalPosts() {
  const byId = new Map();
  let names;
  try {
    names = await readdir(POSTS_DIR);
  } catch (err) {
    fail(`Cannot read ${POSTS_DIR}: ${err?.message ?? err}`);
  }
  for (const name of names.sort()) {
    if (!name.endsWith('.json')) continue;
    if (name.toLowerCase().includes('example')) continue;
    const filePath = path.join(POSTS_DIR, name);
    let item;
    try {
      item = JSON.parse(await readFile(filePath, 'utf8'));
    } catch {
      continue;
    }
    const id = stableExternalId(item);
    if (!id) continue;
    if (byId.has(id)) {
      fail(`Duplicate local externalId "${id}" in ${path.basename(byId.get(id).filePath)} and ${name}`);
    }
    byId.set(id, { filePath, item });
  }
  return byId;
}

function summarize(item) {
  return {
    externalId: item.externalId ?? item.external_id ?? item.id ?? null,
    slug: item.slug ?? null,
    title: item.title ?? null,
    period: item.period ?? item.month ?? null,
  };
}

// --- fetch ----------------------------------------------------------------
const base = DASHBOARD_URL.replace(/\/+$/, '');
const url = new URL(`${base}/api/content`);
url.searchParams.set('brand', brand);
url.searchParams.set('status', 'approved');

let res;
try {
  res = await fetch(url, {
    method: 'GET',
    headers: { 'x-ingest-key': WD_INGEST_KEY },
  });
} catch (err) {
  fail(`Network error GETting ${url}: ${err?.message ?? err}`);
}

const text = await res.text();
let payload;
try {
  payload = JSON.parse(text);
} catch {
  payload = null;
}

if (!res.ok) {
  console.error(payload ?? text);
  fail(`Dashboard returned ${res.status} ${res.statusText}. Auth/API error — not publishing.`);
}

const rawItems = asItems(payload);
if (!rawItems) {
  console.error(payload ?? text);
  fail('Dashboard response was not a content list (expected an array or { items|content|data|results }).');
}

let hubItems = rawItems;
if (cliPeriod) {
  hubItems = hubItems.filter((item) => (item.period ?? item.month) === cliPeriod);
}

// --- list mode ------------------------------------------------------------
if (!doCheck && !doApply) {
  const items = hubItems.map(summarize);
  const report = {
    brand,
    status: 'approved',
    period: cliPeriod || null,
    count: items.length,
    items,
  };

  if (outPath) {
    await writeFile(outPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
    console.error(`[pull:approved] wrote ${outPath}`);
  }

  if (asJson) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    const scope = cliPeriod ? ` period=${cliPeriod}` : '';
    console.log(`[pull:approved] brand="${brand}" status=approved${scope} count=${items.length}`);
    if (!items.length) {
      console.log('(none)');
    } else {
      for (const item of items) {
        console.log(
          `  - externalId=${item.externalId ?? '—'}  slug=${item.slug ?? '—'}  title=${item.title ?? '—'}  period=${item.period ?? '—'}`,
        );
      }
    }
    console.log('\n[pull:approved] Approved = ready for the publish pipeline (not live). This script does not publish.');
    console.log('[pull:approved] For reviewer edits: --check (diff) or --apply (write hub → local). Do not re-ingest after apply.');
  }

  if (failIfNone && items.length === 0) {
    fail(`No approved content for brand="${brand}"${cliPeriod ? ` period=${cliPeriod}` : ''}.`);
  }
  process.exit(0);
}

// --- check / apply --------------------------------------------------------
const localById = await indexLocalPosts();
const counts = { unchanged: 0, updated: 0, 'missing-local': 0, 'missing-externalId': 0 };
const rows = [];

for (const hub of hubItems) {
  const mapped = hubFields(hub);
  if (!mapped.externalId) {
    counts['missing-externalId'] += 1;
    rows.push({
      status: 'missing-externalId',
      title: mapped.title,
      slug: mapped.slug,
      period: mapped.period,
    });
    continue;
  }

  const localEntry = localById.get(mapped.externalId);
  if (!localEntry) {
    counts['missing-local'] += 1;
    rows.push({
      status: 'missing-local',
      externalId: mapped.externalId,
      title: mapped.title,
      slug: mapped.slug,
      period: mapped.period,
    });
    continue;
  }

  const local = localFields(localEntry.item);
  const diffs = fieldDiffs(local, mapped);
  const rel = path.relative(REPO_ROOT, localEntry.filePath);

  if (!diffs.length) {
    counts.unchanged += 1;
    rows.push({
      status: 'unchanged',
      externalId: mapped.externalId,
      file: rel,
      title: mapped.title,
      slug: mapped.slug,
      period: mapped.period,
    });
    continue;
  }

  if (doApply) {
    const next = { ...localEntry.item };
    next.title = mapped.title;
    next.slug = mapped.slug;
    next.content = mapped.content;
    if (mapped.focus_keyword != null) next.focus_keyword = mapped.focus_keyword;
    if (mapped.period) next.period = mapped.period;
    // Keep meta_title aligned with hub title when it still mirrored the old title.
    if (mapped.title && (!next.meta_title || next.meta_title === local.title)) {
      next.meta_title = mapped.title;
    }
    await writeFile(localEntry.filePath, `${JSON.stringify(next, null, 2)}\n`, 'utf8');
  }

  counts.updated += 1;
  rows.push({
    status: 'updated',
    externalId: mapped.externalId,
    file: rel,
    title: mapped.title,
    slug: mapped.slug,
    period: mapped.period,
    diffs,
    applied: doApply,
  });
}

const report = {
  brand,
  status: 'approved',
  mode: doApply ? 'apply' : 'check',
  period: cliPeriod || null,
  counts,
  rows,
};

if (outPath) {
  await writeFile(outPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.error(`[pull:approved] wrote ${outPath}`);
}

if (asJson) {
  console.log(JSON.stringify(report, null, 2));
} else {
  const scope = cliPeriod ? ` period=${cliPeriod}` : '';
  const verb = doApply ? 'apply' : 'check';
  console.log(`[pull:approved] ${verb} brand="${brand}" status=approved${scope}`);
  console.log(
    `  unchanged=${counts.unchanged}  updated=${counts.updated}  missing-local=${counts['missing-local']}  missing-externalId=${counts['missing-externalId']}`,
  );
  for (const row of rows) {
    if (row.status === 'unchanged') {
      console.log(`  ✓ ${row.externalId}  ${row.file}  (unchanged)`);
    } else if (row.status === 'updated') {
      const label = row.applied ? 'updated' : 'needs-update';
      console.log(`  → ${row.externalId}  ${row.file}  (${label}: ${row.diffs.join(', ')})`);
    } else if (row.status === 'missing-local') {
      console.log(`  ✗ ${row.externalId}  missing-local (no content/posts match)`);
    } else {
      console.log(`  ✗ missing-externalId  title=${row.title ?? '—'} slug=${row.slug ?? '—'}`);
    }
  }
  console.log('\n[pull:approved] Hub is source of truth for approved posts until publish.');
  if (doApply) {
    console.log('[pull:approved] Applied hub fields to local JSON. Publish from local files — do NOT re-ingest (resets to in_review).');
  } else {
    console.log('[pull:approved] Check only — no files written. Use --apply to write hub → local.');
  }
  console.log('[pull:approved] This script does not publish live.');
}

if (failIfNone && hubItems.length === 0) {
  fail(`No approved content for brand="${brand}"${cliPeriod ? ` period=${cliPeriod}` : ''}.`);
}

const hasGaps = counts['missing-local'] > 0 || counts['missing-externalId'] > 0;
if (doCheck && (counts.updated > 0 || hasGaps)) {
  process.exit(1);
}
if (doApply && hasGaps) {
  process.exit(1);
}
