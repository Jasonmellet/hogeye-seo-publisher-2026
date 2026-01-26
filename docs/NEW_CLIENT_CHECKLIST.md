# New Client Checklist (TTT SEO Publisher)

This checklist is the fastest path to get a new client (e.g. Hogeye Cameras, Big Pig Traps) running with this repo.

## 1) Local setup

- Create `.env` from `env.example` and fill in:
  - `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
  - `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`
  - `SEO_SPREADSHEET_ID` (planning sheet)
  - `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON path)
  - Optional: `GSC_SITE_URL`, `GA4_PROPERTY_ID`

## 2) Google access (one-time per client)

- Enable APIs in Google Cloud:
  - Search Console API
  - Google Analytics Data API
  - Google Sheets API
  - Google Drive API (recommended)
- Grant the service account email access to:
  - GSC property (at least Performance read)
  - GA4 property (Viewer/Analyst)

See `docs/GOOGLE_CLOUD_API_ENABLEMENT.md`.

## 3) Smoke tests

- WordPress connectivity:

```bash
./.venv/bin/python scripts/test_connection.py
```

- DataForSEO connectivity:

```bash
./.venv/bin/python scripts/seo/dataforseo_benchmark_rank_snapshot.py --project-root "$(pwd)" --max-keywords 5 --output-dir "work/seo/benchmark/smoke"
```

## 4) “No-GSC-needed” research you can run immediately

Pick a short client key (examples: `hogeye`, `bpt`, `bb`) and run:

```bash
./.venv/bin/python scripts/seo/ttt_build_keyword_universe.py --client-key hogeye
./.venv/bin/python scripts/seo/ttt_serp_competitors_snapshot.py --client-key hogeye
./.venv/bin/python scripts/seo/ttt_backlinks_gap.py --client-key hogeye
./.venv/bin/python scripts/seo/ttt_build_roadmap_template.py --client-key hogeye --year 2026
```

All outputs land in `work/seo/plan/` and are git-ignored.

## 5) Benchmarks (best effort, works partially without Google)

Generate benchmark CSVs:

```bash
./.venv/bin/python scripts/seo/run_benchmark.py --project-root "$(pwd)" --allow-partial --skip-gsc --skip-ga4
```

When GSC/GA4 access is ready, re-run without skip flags and push tabs to Sheets.
