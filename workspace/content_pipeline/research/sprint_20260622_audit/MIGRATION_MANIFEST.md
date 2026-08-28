# Migration manifest — Advanced SEO Analysis → HogEye Content Publisher

**Migrated:** 2026-06-23 (gap fill same day)

---

## Carried over (complete)

### HogEye findings & synthesis (`findings/`)

All 12 markdown outputs from audit `clients/hogeye/outputs/`:

- `technical-findings.md` (June 2026 SF)
- `gsc-findings.md`, `ga4-findings.md`
- `dataforseo-research-plan.md`, `dataforseo-research-summary.md`
- `content-strategy-opportunities.md`
- `competitive-landscape.md`, `keyword-opportunities.md`, `search-opportunities.md`
- `final-audit.md`, `technical-findings-old.md`, `README.md`

### HogEye working context (`working/`)

- `audit-doc-roadmap.md`, `screwworm-content-guidelines.md`
- `sf-crawl-2026-06-22.md`, `gsc-dataforseo-seeds.json`
- `client-facts.md`, `findings.md`, `assumptions-and-unknowns.md`
- `data-intake-checklist.md`
- `dataforseo-run.log`, `dataforseo-queue.log` (run provenance)

### Config (`config/`)

- `client_config.yaml`, `niche_config.yaml`

### Primary datasets (`inputs/`)

| Dataset | Files |
| ------- | ----- |
| GSC | `Queries.csv`, `Pages.csv`, `Performance_by_date.csv`, `README.md` |
| GA4 | All 6 CSV exports (through 2026-06-21 pull) |
| DataForSEO | `dataforseo_hogeye_raw.json`, archive `*.2026-06-22T23-40-19Z.json`, `dataforseo_hogeye_wildlife_dominion.json`, `dataforseo_hogeye_raw.previous.json` (April archive) |

### Screaming Frog (June 2026)

Full export (16 files): `work/seo/screaming_frog/2026.06.22.agt-cursor/`

### Wildlife Dominion portfolio (`stakeholder/` + `stakeholder/wildlife-dominion/`)

- Sprint contract, screwworm matrix, Google pull summary (top level)
- `google-access-status.md`, `google-access-probe.json`
- `data-intake-checklist.md`, `analysis-summary.json`, `dataforseo-summary.json`
- `before-after-seo-report.md`
- `wildlife_dominion_dataforseo_raw.json`

### Created in Content Publisher (not in audit repo)

- `INDEX.md`, `inputs.json`, this manifest
- July 2026 plan: `workspace/content_pipeline/monthly/2026-07/`

---

## Intentionally not duplicated

| Item | Reason | Still available |
| ---- | ------ | --------------- |
| April 2026 SF crawl (~685 files) | Baseline only; huge | Advanced SEO Analysis `clients/hogeye/inputs/screaming_frog/2026.04.09.05.15.26/` |
| May 2026 SF crawl in publisher | Already existed pre-migration | `work/seo/screaming_frog/2026.05.21.07.33.25-agt-hogeye/` |
| `.gitkeep` placeholders | Empty | — |
| Audit repo Python runners | Execution tooling stays in audit repo | `Advanced SEO Analysis/analysis/` |

---

## Coverage summary

| Category | Status |
| -------- | ------ |
| Decision docs (findings, strategy, plan) | ✅ 100% |
| GSC / GA4 CSVs used in sprint | ✅ 100% |
| DataForSEO raw (current + archives) | ✅ 100% |
| June SF crawl | ✅ 100% |
| WD stakeholder / portfolio context | ✅ 100% |
| Run logs & intake checklists | ✅ 100% |
| April SF bulk exports | ⚠️ Reference only (audit repo) |
| Content calendar / briefs | ✅ Started in publisher (`2026-07/`) |

**Bottom line:** All **content and context needed to plan and write** is in this repo. Historical April crawl bulk stays in the audit repo by design (documented in `INDEX.md`).
