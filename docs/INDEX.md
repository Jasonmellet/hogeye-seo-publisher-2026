# Documentation index

All hand-written docs for this repo live under **`docs/`** (this file is the map).

**Shared AGT playbooks:** [AGT Docs Hub](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/overview) (SEO Research Module, DataForSEO quality bar, monthly cycle, draft-first CMS). Do not fork those quality bars into `docs/`.

## Essentials

- **Monthly cycle (canonical):** [`MONTHLY_PUBLISHING_WORKFLOW.md`](MONTHLY_PUBLISHING_WORKFLOW.md) + [`.cursor/skills/he-monthly-cycle/SKILL.md`](../.cursor/skills/he-monthly-cycle/SKILL.md)
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

## Technical SEO (Screaming Frog)

- **MCP setup (HogEye):** [`SCREAMING_FROG_MCP.md`](SCREAMING_FROG_MCP.md)
- **Tracker + comparison crawls:** [`../workspace/technical_seo/README.md`](../workspace/technical_seo/README.md)
- **Crawl exports (local, gitignored):** [`../work/seo/screaming_frog/README.md`](../work/seo/screaming_frog/README.md)

## Cursor / AI agents

- [`agents/README.md`](agents/README.md) — when to use which persona
- [`agents/AGENT_LIBRARIAN.md`](agents/AGENT_LIBRARIAN.md)
- [`agents/AGENT_SEO_MONITOR.md`](agents/AGENT_SEO_MONITOR.md)
- Humanizer (punctuation + voice pass): [`../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`](../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md)

## Execution & planning

- **Monthly publishing (hub → pull/apply → WP draft → email):** [`MONTHLY_PUBLISHING_WORKFLOW.md`](MONTHLY_PUBLISHING_WORKFLOW.md)
- **Publish safety (HogEye WP detail):** [`PUBLISH_SAFETY_MANDATE.md`](PUBLISH_SAFETY_MANDATE.md) — shared rules: [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684/Draft-first+CMS+publishing)
- **Roadmap**: [`ROADMAP.md`](ROADMAP.md)
- **Project status (HogEye):** [`HOGEYE_PROJECT_STATUS.md`](HOGEYE_PROJECT_STATUS.md) — July live; August WP drafts
- **June batch detail:** [`../workspace/content_pipeline/monthly/2026-06/STATUS.md`](../workspace/content_pipeline/monthly/2026-06/STATUS.md)
- **Security**: [`SECURITY.md`](SECURITY.md)
- **Troubleshooting WP auth**: [`CONNECTION_DIAGNOSTIC.md`](CONNECTION_DIAGNOSTIC.md)
- **Backup/restore**: [`BACKUP_RESTORE.md`](BACKUP_RESTORE.md)
- **New client checklist**: [`NEW_CLIENT_CHECKLIST.md`](NEW_CLIENT_CHECKLIST.md)
- **Google API enablement**: [`GOOGLE_CLOUD_API_ENABLEMENT.md`](GOOGLE_CLOUD_API_ENABLEMENT.md)

## SEO planning (Sheets / Semrush / DataForSEO)

- **Shared research + $10-tier quality bar:** [SEO Research Module](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65663/SEO+Research+Module) · [DataForSEO quality bar](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/327752/DataForSEO+quality+bar)
- **SEO metadata status**: [`SEO_METADATA_STATUS.md`](SEO_METADATA_STATUS.md)
- **Tech spec (publisher)**: [`TECH_SPEC.md`](TECH_SPEC.md)
- **Note**: This repo assumes a paid DataForSEO plan is available (Keywords/SERP + Backlinks; AI Optimization optional). Configure via `.env` (`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`).
- **DataForSEO API Bible** (vendor endpoint reference for this repo): [`DATAFORSEO_BIBLE.md`](DATAFORSEO_BIBLE.md)

## Benchmarking (present-state baseline)

- **One-command runner**: [`../scripts/seo/run_benchmark.py`](../scripts/seo/run_benchmark.py)
- **Outputs**: `work/seo/benchmark/YYYY-MM-DD/` pushed into sheet tabs:
  - `Benchmark_Summary`
  - `Benchmark_GSC_LandingPages`
  - `Benchmark_GSC_QueriesByPage`
  - `Benchmark_GA4_LandingPages`
  - `Benchmark_DataForSEO_RankSnapshot`
