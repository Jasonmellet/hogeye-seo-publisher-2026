# Starter (run this in every new client repo)

This file is the “context + checklist” for both:

- You (operator) running the repo, and
- Any Cursor AI agent helping inside this repo.

If an agent feels lost, tell it: **Read `starter.md` first, then follow the canonical scripts only.**

---

## Operator preference (IMPORTANT)

You (the operator) do **not** want to run terminal commands manually.

If you are a Cursor AI agent working in this repo:

- Ask for confirmation before doing anything that writes (publishing to WP, updating WP content, modifying files).
- Then execute the steps yourself using Cursor’s tools/terminal.
- Prefer draft-first. Do not publish live unless explicitly confirmed.

---

## What this repo is (mental model)

This repo has two engines:

1) **WordPress Publishing Engine**

- Input: JSON files in `content/posts/*.json` and `content/pages/*.json`
- Output: draft-first updates in WordPress via REST API
- Canonical entrypoints:
  - `publish_content_item.py` (one file)
  - `publish_batch.py` (directory or list of files)

2) **SEO Planning Engine (optional / enabled when configured)**

- Input: CSVs under `work/seo/...` (Semrush/GSC/GA4/DataForSEO)
- Output: a Google Sheet planning spreadsheet via `scripts/seo/*`

---

## Non-negotiable safety rules (read this)

- Never commit `.env` (it contains credentials). `.env` is git-ignored.
- Always create `client.config.json` (safe to commit). It prevents wrong-site publishing.
- Default workflow is draft-first. Do not publish live until reviewed in WP admin.
- Use canonical scripts only:
  - ✅ `publish_content_item.py`
  - ✅ `publish_batch.py`
  - ✅ `test_connection.py`
  - ⚠️ `resolve_internal_links.py` (site-wide mutation; use `--dry-run` first)
  - ❌ avoid `scripts/legacy/*` for normal monthly publishing

---

## 0) Local folder strategy (recommended with Cursor)

Create a parent folder, then 1 repo folder per client:

- `~/Desktop/seo-clients/camp-lakota-seo-publisher`
- `~/Desktop/seo-clients/boar-blanket-seo-publisher`
- `~/Desktop/seo-clients/hog-eye-cameras-seo-publisher`

Open one repo folder per Cursor project (keeps `.env`, `work/`, and content isolated).

---

## 1) Clone + open in Cursor

```bash
mkdir -p ~/Desktop/seo-clients
cd ~/Desktop/seo-clients
git clone YOUR_GITHUB_REPO_URL_HERE
cd YOUR_REPO_FOLDER_NAME
```

Then open that folder in Cursor: File → Open Folder.

---

## 2) Install (one time per client repo)

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

---

## 3) Create config files (required)

```bash
cp env.example .env
cp client.config.example.json client.config.json
```

### 3a) Edit `.env` (local-only secrets)

Must set:

- `WP_SITE_URL=https://client-site.com` (no trailing slash)
- `WP_USERNAME=...`
- `WP_APP_PASSWORD=.... .... ....` (WordPress Application Password with spaces)

Recommended during setup:

- `DRY_RUN=true` (safe rehearsal; no WordPress writes)

### 3b) Edit `client.config.json` (commit-safe guardrail)

Must set:

- `clientName`: exact human name (used for confirmation if you publish)
- `expectedWpSiteUrl`: must match `.env` `WP_SITE_URL`
- `expectedWpSiteHost`: hostname only (e.g. `example.com`)

Optional but recommended:

- `expectedWpSiteName`: WP “Site Title” for an extra mismatch check
- `protectedMarkersBySlug`: markers that must not disappear when updating a given page slug
- `linkAliases`: slug→absolute URL aliases for link resolution (`{{link:slug}}`)

---

## 4) Verify WordPress connection (read-only)

```bash
./.venv/bin/python test_connection.py
```

If this fails, do not proceed. Fix `.env` first.

---

## 5) Publishing workflow (the only supported way)

### Step 1: Dry run validation (no WP writes)

Set `DRY_RUN=true` in `.env`, then:

```bash
./.venv/bin/python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts
```

### Step 2: Draft-first write (creates/updates drafts in WordPress)

Set `DRY_RUN=false` in `.env`, keep status as draft:

```bash
./.venv/bin/python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts --status draft
```

### Step 3: Review in WP admin (manual)

Check:

- Formatting (mobile + desktop)
- Images look correct
- SEO title/description populated
- No `{{link:...}}` placeholders remain (or accept warnings until later)

### Step 4: Publish live (explicit action)

Only after review:

```bash
./.venv/bin/python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts --status publish
```

Notes:

- When you publish, the script forces a safety confirmation unless you pass `--yes`.
- `--yes` exists for automation; don’t use it casually.

---

## 6) Internal links (`{{link:...}}`)

Two supported approaches:

1) Resolve while publishing (recommended when target slugs already exist in WP):

```bash
./.venv/bin/python publish_content_item.py /abs/path/to/file.json --type posts --resolve-links
```

2) Resolve across existing WP content (site-wide tool):

```bash
./.venv/bin/python resolve_internal_links.py --dry-run
./.venv/bin/python resolve_internal_links.py
```

If a link slug doesn’t exist yet, add a `linkAliases` entry in `client.config.json`.

---

## 7) SEO workflow (optional)

Required `.env` vars (minimum):

- `SEO_SPREADSHEET_ID`
- `GOOGLE_APPLICATION_CREDENTIALS` (absolute path to service account JSON)
- `GSC_SITE_URL` (example: `sc-domain:example.com`)

Present-state benchmark (recommended first):

```bash
./.venv/bin/python scripts/seo/run_benchmark.py --project-root "$(pwd)" --site-url "$GSC_SITE_URL" --spreadsheet-id "$SEO_SPREADSHEET_ID"
```

Notes:

- GA4 is optional (`GA4_PROPERTY_ID`).
- DataForSEO is optional but recommended. Configure `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` in `.env` to run DataForSEO scripts (Keywords/SERP + Backlinks; AI Optimization optional).

---

## 8) Where did my SEO files go?

The folder `work/` is git-ignored by design.

- Use it for large local artifacts (CSVs, benchmark outputs, intermediate planning).
- The durable store for planning is usually your Google Sheet.

---

## Common failure modes (fast fixes)

- Wrong-site blocked: `.env` `WP_SITE_URL` doesn’t match `client.config.json` expected URL/host.
- 401 Unauthorized: App Password wrong or missing spaces; regenerate it in WP Admin.
- Service account JSON missing: set `GOOGLE_APPLICATION_CREDENTIALS=/abs/path/to/key.json`.
- SEO scripts can’t find Semrush files: set `SEMRUSH_OTI_DIR` or pass `--semrush-dir`.

