# Documentation index

All hand-written docs for this repo live under **`docs/`** (this file is the map).

## Essentials

- **Operator / agent runbook**: [`starter.md`](starter.md)
- **Quick setup**: [`QUICK_START.md`](QUICK_START.md)
- **Credential intake (short)**: [`STARTUP.md`](STARTUP.md)
- **Per-client setup**: [`CLIENT_SETUP.md`](CLIENT_SETUP.md)
- **WordPress publisher CLIs**: [`../scripts/publisher/README.md`](../scripts/publisher/README.md)
- **Replication guide (patterns)**: [`WORDPRESS_PUBLISHING_REPLICATION_GUIDE.md`](WORDPRESS_PUBLISHING_REPLICATION_GUIDE.md)
- **Repo folders (input / output first)**: [`REPO_LAYOUT.md`](REPO_LAYOUT.md)
- **Input drop zones**: [`../input/README.md`](../input/README.md)
- **Output (drafts + WP JSON shortcuts)**: [`../output/README.md`](../output/README.md)
- **WordPress JSON (canonical `content/` vs `output/wordpress/`)**: [`../content/README.md`](../content/README.md)
- **Monthly folder = publication month?** (`apr26` vs March research, …): [`../workspace/content_pipeline/monthly/README.md`](../workspace/content_pipeline/monthly/README.md)
- **Schell / HogEye owner feedback (Librarian):** [`../workspace/CLIENT_FEEDBACK_SCHELL_APR2026.md`](../workspace/CLIENT_FEEDBACK_SCHELL_APR2026.md)
- **Archived / superseded material (not active workflow)**: [`../archive/README.md`](../archive/README.md)
- **Content-system folder layout + npm commands**: [`knowledge/content-system-replication-guide.md`](knowledge/content-system-replication-guide.md)

## Cursor / AI agents

- [`agents/README.md`](agents/README.md) — when to use which persona
- [`agents/AGENT_LIBRARIAN.md`](agents/AGENT_LIBRARIAN.md)
- [`agents/AGENT_SEO_MONITOR.md`](agents/AGENT_SEO_MONITOR.md)
- Humanizer (punctuation + voice pass): [`../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`](../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md)

## Execution & planning

- **Monthly publishing**: [`MONTHLY_PUBLISHING_WORKFLOW.md`](MONTHLY_PUBLISHING_WORKFLOW.md)
- **Roadmap**: [`ROADMAP.md`](ROADMAP.md)
- **Project status**: [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- **Security**: [`SECURITY.md`](SECURITY.md)
- **Troubleshooting WP auth**: [`CONNECTION_DIAGNOSTIC.md`](CONNECTION_DIAGNOSTIC.md)
- **Backup/restore**: [`BACKUP_RESTORE.md`](BACKUP_RESTORE.md)
- **New client checklist**: [`NEW_CLIENT_CHECKLIST.md`](NEW_CLIENT_CHECKLIST.md)
- **Google API enablement**: [`GOOGLE_CLOUD_API_ENABLEMENT.md`](GOOGLE_CLOUD_API_ENABLEMENT.md)

## SEO planning (Sheets / Semrush / DataForSEO)

- **SEO metadata status**: [`SEO_METADATA_STATUS.md`](SEO_METADATA_STATUS.md)
- **Tech spec (publisher)**: [`TECH_SPEC.md`](TECH_SPEC.md)
- **Note**: This repo assumes a paid DataForSEO plan is available (Keywords/SERP + Backlinks; AI Optimization optional). Configure via `.env` (`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`).
- **DataForSEO API Bible**: [`DATAFORSEO_BIBLE.md`](DATAFORSEO_BIBLE.md)

## Benchmarking (present-state baseline)

- **One-command runner**: [`../scripts/seo/run_benchmark.py`](../scripts/seo/run_benchmark.py)
- **Outputs**: `work/seo/benchmark/YYYY-MM-DD/` pushed into sheet tabs:
  - `Benchmark_Summary`
  - `Benchmark_GSC_LandingPages`
  - `Benchmark_GSC_QueriesByPage`
  - `Benchmark_GA4_LandingPages`
  - `Benchmark_DataForSEO_RankSnapshot`
