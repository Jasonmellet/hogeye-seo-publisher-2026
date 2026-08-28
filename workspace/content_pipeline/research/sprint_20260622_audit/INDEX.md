# HogEye SEO sprint research — June 2026 audit intake

**Migrated:** 2026-06-23  
**Source repo:** Advanced SEO Analysis → `clients/hogeye/`  
**Purpose:** Single research bundle for July 2026+ content planning in **this** repo.

---

## What this folder contains

| Path | Contents |
| ---- | -------- |
| `findings/` | All synthesis docs (SF, GSC, GA4, DataForSEO plan + summary, content strategy) |
| `working/` | Roadmap, screwworm guidelines, GSC→DataForSEO seeds, client facts |
| `stakeholder/` | WD sprint brief, screwworm topic matrix, Google pull summary |
| `config/` | `client_config.yaml`, `niche_config.yaml` (DataForSEO $10 tier run) |
| `inputs/gsc/` | Queries, Pages, Performance_by_date CSVs (through 2026-06-21) |
| `inputs/ga/` | GA4 traffic + landing exports |
| `inputs/dataforseo/` | Full raw bundle ($7.08) + archive + WD supplement |
| `inputs.json` | Machine-readable manifest + pass/fail metrics |

**Screaming Frog exports (June 2026):**  
`work/seo/screaming_frog/2026.06.22.agt-cursor/` (not duplicated here — local crawl work folder)

---

## Read order (agents + humans)

1. `findings/content-strategy-opportunities.md` — **what to publish next**
2. `findings/dataforseo-research-summary.md` — SERP/LLM/ChatGPT evidence
3. `findings/gsc-findings.md` + `findings/ga4-findings.md` — search + analytics reality
4. `findings/technical-findings.md` — fix before/at scale (`/trap-camera/` 404, H1, buy-now)
5. `stakeholder/content-sprint-stakeholder-brief-2026-06.md` — contract volume, screwworm rules, geo weights
6. `working/screwworm-content-guidelines.md` — HE-specific screwworm angle

---

## DataForSEO run (Phase 6 complete)

| Metric | Value |
| ------ | ----- |
| Spend | **$7.08** |
| SERP checks | **320** (depth 20; 81 GSC-forced extras) |
| LLM mentions | **45** |
| ChatGPT tasks | **28** (HE cited **7/28**) |
| Merged keywords | **355** (strict hog/trap/camera niche gate) |
| Archive | `inputs/dataforseo/dataforseo_hogeye_raw.2026-06-22T23-40-19Z.json` |

---

## Content planning lives here now

- **July 2026 plan:** `workspace/content_pipeline/monthly/2026-07/CONTENT_PLAN.md`
- **Queue:** `workspace/content_pipeline/monthly/2026-07/queue/monthly_queue.csv`
- **Execution tracker:** `workspace/EXECUTION_STATUS.md`

Do **not** build new calendars in Advanced SEO Analysis — that repo remains the audit/analysis engine; **this repo owns publishing workflow**.

---

## Source-of-truth map

| Topic | Authoritative copy (this repo) | Original audit path |
| ----- | ------------------------------ | ------------------- |
| Findings markdown | `findings/*.md` | `Advanced SEO Analysis/clients/hogeye/outputs/` |
| Raw DataForSEO | `inputs/dataforseo/` | same under audit `inputs/dataforseo/` |
| GSC/GA CSVs | `inputs/gsc/`, `inputs/ga/` | audit `inputs/` |
| SF June crawl | `work/seo/screaming_frog/2026.06.22.agt-cursor/` | audit `inputs/screaming_frog/` |

Re-sync from audit repo only when a **new** analysis phase completes — copy into a new dated `sprint_*` folder; do not edit audit inputs in place from here.
