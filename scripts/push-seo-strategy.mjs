#!/usr/bin/env node
// Push ./SEO_STRATEGY.md to the Wildlife Dominion brand portal.
// Re-running updates the same doc in place (keyed by brand on the dashboard).
//
// Required env (from gitignored .env locally, or CI/repo secrets):
//   DASHBOARD_URL   e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev
//   WD_INGEST_KEY   secret ingest key (never commit)
import 'dotenv/config';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const BRAND = 'hogeye-cameras';
const TITLE = 'HogEye Cameras SEO Strategy';
const STRATEGY_PATH = fileURLToPath(new URL('../SEO_STRATEGY.md', import.meta.url));

function fail(message) {
  console.error(`\n[push:strategy] ${message}\n`);
  process.exit(1);
}

const { DASHBOARD_URL, WD_INGEST_KEY } = process.env;

if (!DASHBOARD_URL) {
  fail('Missing DASHBOARD_URL. Set it in a gitignored .env or CI secret (e.g. https://wildlife-dominion-dashboard.jason-17f.workers.dev).');
}
if (!WD_INGEST_KEY) {
  fail('Missing WD_INGEST_KEY. Set it in a gitignored .env or CI secret — never commit this value.');
}

let bodyMd;
try {
  bodyMd = await readFile(STRATEGY_PATH, 'utf8');
} catch (err) {
  if (err && err.code === 'ENOENT') {
    fail(`Missing SEO_STRATEGY.md at repo root (${STRATEGY_PATH}). Create it before pushing.`);
  }
  fail(`Could not read SEO_STRATEGY.md: ${err?.message ?? err}`);
}

if (!bodyMd.trim()) {
  fail(`SEO_STRATEGY.md is empty (${STRATEGY_PATH}). Add content before pushing.`);
}

const endpoint = `${DASHBOARD_URL.replace(/\/+$/, '')}/api/ingest/strategy`;

let res;
try {
  res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'x-ingest-key': WD_INGEST_KEY,
      'content-type': 'application/json',
    },
    body: JSON.stringify({ brand: BRAND, title: TITLE, bodyMd }),
  });
} catch (err) {
  fail(`Network error POSTing to ${endpoint}: ${err?.message ?? err}`);
}

const text = await res.text();
let payload;
try {
  payload = JSON.parse(text);
} catch {
  payload = text;
}

console.log(`[push:strategy] POST ${endpoint} -> ${res.status} ${res.statusText}`);
console.log(typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2));

if (!res.ok) {
  fail(`Dashboard returned non-2xx status ${res.status}. See response above.`);
}

console.log(`[push:strategy] Published "${TITLE}" for brand "${BRAND}".`);
