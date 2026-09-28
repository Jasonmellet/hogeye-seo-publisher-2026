#!/usr/bin/env node
// Record live URLs with the hub for approved posts that are now live on WordPress.
// The hub marks each one published and starts article performance (Search Console + GA4).
//
// Dry-run by default: lists approved hub items and their live WordPress URL, if any.
// --write POSTs each live URL to /api/content/:id/published.
//
// Usage:
//   npm run mark:live [-- --period 2026-09]
//   npm run mark:live -- --write [--period 2026-09]
//
// Env (.env): DASHBOARD_URL, WD_INGEST_KEY, WD_BRAND, WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD

import 'dotenv/config';

const DEFAULT_BRAND = 'hogeye-cameras';

function fail(message) {
  console.error(`\n[mark:live] ${message}\n`);
  process.exit(1);
}

function env(name) {
  const value = process.env[name]?.trim();
  if (!value) fail(`${name} is not set. Add it to .env.`);
  return value;
}

const argv = process.argv.slice(2);
let write = false;
let period = null;
for (let i = 0; i < argv.length; i += 1) {
  const a = argv[i];
  if (a === '--write') write = true;
  else if (a === '--period') period = argv[++i];
  else if (a.startsWith('--period=')) period = a.slice('--period='.length);
  else fail(`Unknown argument: ${a}`);
}
if (period && !/^\d{4}-\d{2}$/.test(period)) fail(`--period must be YYYY-MM (got "${period}").`);

const brand = (process.env.WD_BRAND || DEFAULT_BRAND).trim();
const dashboard = env('DASHBOARD_URL').replace(/\/$/, '');
const ingestKey = env('WD_INGEST_KEY');
const site = env('WP_SITE_URL').replace(/\/$/, '');
const wpAuth = `Basic ${Buffer.from(`${env('WP_USERNAME')}:${env('WP_APP_PASSWORD')}`).toString('base64')}`;

// Published post or page with this slug, or null if it is not live yet.
async function findLive(slug) {
  for (const type of ['posts', 'pages']) {
    const url = `${site}/wp-json/wp/v2/${type}?slug=${encodeURIComponent(slug)}&status=publish&_fields=id,link`;
    const res = await fetch(url, { headers: { Authorization: wpAuth } });
    if (!res.ok) fail(`WordPress GET ${type}?slug=${slug} → ${res.status}: ${(await res.text()).slice(0, 300)}`);
    const [hit] = await res.json();
    if (hit?.link) return hit.link;
  }
  return null;
}

const params = new URLSearchParams({ brand, status: 'approved' });
if (period) params.set('period', period);
const listRes = await fetch(`${dashboard}/api/content?${params}`, { headers: { 'x-ingest-key': ingestKey } });
if (!listRes.ok) fail(`Dashboard returned ${listRes.status}: ${(await listRes.text()).slice(0, 300)}`);
const body = await listRes.json();
const items = Array.isArray(body) ? body : body?.items ?? [];

console.log(`[mark:live] Approved hub items for ${brand}: ${items.length}${write ? '' : ' (dry run)'}\n`);
let recorded = 0;
for (const item of items) {
  if (!item.slug) {
    console.log(`  skip     | ${item.externalId ?? item.id} | no slug`);
    continue;
  }
  const live = await findLive(item.slug);
  if (!live) {
    console.log(`  not live | ${item.slug}`);
    continue;
  }
  if (!write) {
    console.log(`  live     | ${item.slug} | ${live}`);
    continue;
  }
  const res = await fetch(`${dashboard}/api/content/${item.id}/published`, {
    method: 'POST',
    headers: { 'x-ingest-key': ingestKey, 'content-type': 'application/json' },
    body: JSON.stringify({ url: live }),
  });
  if (!res.ok) {
    console.log(`  FAILED   | ${item.slug} | HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
    continue;
  }
  recorded += 1;
  console.log(`  recorded | ${item.slug} | ${live}`);
}

if (write) console.log(`\n[mark:live] Recorded ${recorded} live URL(s) with the hub.`);
else console.log('\n[mark:live] Dry run — nothing recorded. Re-run with --write to mark live posts published in the hub.');
