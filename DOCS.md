# Documentation Index

All documentation lives in `docs/`. Start here:

- **Quick start**: `docs/QUICK_START.md`
- **Monthly execution**: `docs/MONTHLY_PUBLISHING_WORKFLOW.md`
- **Roadmap**: `docs/ROADMAP.md`
- **Project status**: `docs/PROJECT_STATUS.md`
- **Security**: `docs/SECURITY.md`
- **Troubleshooting WP auth**: `docs/CONNECTION_DIAGNOSTIC.md`
- **Backup/restore**: `docs/BACKUP_RESTORE.md`
- **New client checklist**: `docs/NEW_CLIENT_CHECKLIST.md`
- **Google API enablement**: `docs/GOOGLE_CLOUD_API_ENABLEMENT.md`

SEO planning (Sheets/Semrush/DataForSEO):

- **SEO metadata status**: `docs/SEO_METADATA_STATUS.md`
- **Tech spec (publisher)**: `docs/TECH_SPEC.md`
- **Note**: This repo assumes a paid DataForSEO plan is available (Keywords/SERP + Backlinks; AI Optimization optional). Configure via `.env` (`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`).
- **DataForSEO API Bible**: `docs/DATAFORSEO_BIBLE.md`

Benchmarking (present-state baseline):

- **One-command runner**: `scripts/seo/run_benchmark.py`
- **Outputs**: `work/seo/benchmark/YYYY-MM-DD/` pushed into sheet tabs:
  - `Benchmark_Summary`
  - `Benchmark_GSC_LandingPages`
  - `Benchmark_GSC_QueriesByPage`
  - `Benchmark_GA4_LandingPages`
  - `Benchmark_DataForSEO_RankSnapshot`
