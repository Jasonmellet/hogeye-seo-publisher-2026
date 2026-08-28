# DataForSEO research plan — HogEye Cameras

**Client:** HogEye (`hogeye`)  
**Document:** DataForSEO API research plan (pre-execution)  
**Created:** 2026-06-22  
**Status:** **Plan only — do not execute until approved**

## Purpose

Define an **extensive, evidence-backed** DataForSEO run that completes the dataset **after** Screaming Frog, GSC, and GA4 — and **before** any content calendar or blog briefs.

This plan merges:

| Source | Role in seeding API calls |
| ------ | ------------------------- |
| **Screaming Frog** (`2026.06.22.agt-cursor`) | URL inventory, 404s, H1/meta gaps, Buy Now thin page |
| **GSC** (`outputs/gsc-findings.md`) | Brand vs non-brand, strikers, low-CTR URLs, comparison gaps |
| **GA4** (`outputs/ga4-findings.md`) | Channel reality, landing targets, revenue tagging gaps |
| **`niche_config.yaml`** | Existing seeds, competitors, niche filter |
| **Stakeholder brief** | Screwworm cadence, geo weighting (TX 40%; MS/LA/OK/AL 60%) |

**Prior pull (baseline only, not sufficient for sprint):**

- `inputs/dataforseo/dataforseo_hogeye_raw.json` (legacy `_dataforseo_hogeye_run.py` bundle)

---

## Execution principles

1. **GSC-validated queries first** — SERP/LLM calls trace to impressions, strikers, or approved seeds.
2. **Update before create** — `/trap-camera/` is **404** in SF but earns GSC clicks; `/blog-4g-vs-5g-…` has **7,454** impressions / **0.25%** CTR — prioritize refresh map.
3. **Geo batch weighted to ad spend** — TX, MS, LA, OK, AL.
4. **Screwworm is greenfield** — **0** GSC queries; full Labs + LLM expansion.
5. **No API spend until this plan is approved** — dry-run first.

**Default API parameters:**

| Parameter | Value |
| --------- | ----- |
| `location_code` | **2840** (United States) |
| `language_code` | **en** |
| Domain target | **hogeyecameras.com** |

**Credentials:** `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` in project `.env`.

**Runners:**

- Preferred: `python3 analysis/dataforseo_niche_bundle.py --client hogeye --dry-run` then full run
- Legacy full script: `python3 analysis/_dataforseo_hogeye_run.py` (update seeds from this plan first)

---

## Phase A — Labs domain footprint

| # | Endpoint | Target | Output use |
| - | -------- | ------ | ---------- |
| A1 | `historical_rank_overview/live` | hogeyecameras.com, vosker.com, reolink.com | Trend vs prior raw JSON |
| A2 | `ranked_keywords/live` | hogeyecameras.com | Map rankings → GSC pages |
| A3 | `relevant_pages/live` | hogeyecameras.com | Labs traffic URL set |
| A4 | `ranked_keywords/live` | vosker.com, reolink.com, spartancamera.com, barnowltech.com | Gap keywords |
| A5 | `competitors_domain/live` | hogeyecameras.com | Discover SERP competitors beyond config list |

**SF cross-check:** URLs with **missing H1** (50% of HTML) that still rank — template fix + content refresh compound priority.

**Estimated tasks:** ~5–8 | **Cost:** Low–medium

---

## Phase B — Keyword expansion

### B1 — GSC striker expansion (non-brand)

Seeds from GSC (0 clicks, position 4–15, impressions ≥ 50):

```
camera hog
hog view
hog cams
wild hog trap monitoring
best camera for hog trapping
smart hog trap technology
hog control system
drop trap camera system
hog cam
satcam
```

Plus click-winners to defend:

```
hog camera
hog trap remote trigger
vosker vs reolink
camera login
```

**Endpoints:** `keyword_suggestions/live`, `related_keywords/live` (depth 2), `search_volume/live` batched.

**Target merged list:** **400–600** unique terms after niche filter (`niche_config.yaml`).

### B2 — Comparison / cellular cluster

```
hogeye vs vosker
hogeye vs reolink
hogeye vs spartan
hogeye vs boarbuster
cellular hog trap camera
4g vs 5g ranch camera
5g cellular monitoring camera
trail camera vs cellular hog trap
reolink go hog trapping
best cellular camera for hog trapping
```

**SF/GSC URL targets:**

- `/blog-hogeye-vs-vosker-cellular-cameras-comparison`
- `/blog-4g-vs-5g-cellular-cameras-ranch-monitoring-2025`
- `/hog-trapping-cameras-compared-2026-hogeye-vs-trail/`
- **Gap:** dedicated Reolink/Spartan/Barn Owl comparison pages

### B3 — Priority state cluster (TX 40%, MS/LA/OK/AL 60%)

| State | Seeds |
| ----- | ----- |
| **Texas** | texas hog trap camera, feral hog monitoring texas, ranch camera texas, hog trap remote trigger texas |
| **Louisiana** | hog traps for sale louisiana, louisiana hog trap camera |
| **Oklahoma** | oklahoma ranch cellular camera, hog trap oklahoma |
| **Mississippi** | mississippi feral hog monitoring, delta ranch camera |
| **Alabama** | alabama hog trap camera, alabama wild hog monitoring |

GSC shows **minimal state query volume** today — treat as **net-new** opportunity.

### B4 — Screwworm / biosecurity (greenfield)

```
what is screwworm
new world screwworm spread
screwworm feral hogs
feral hogs screwworm risk
screwworm cattle ranch texas
wildlife monitoring screwworm
feral hog fly attraction
hog movement disease vector
ranch biosecurity feral hogs
how to spot screwworm
```

**Messaging guardrails:** Stakeholder brief + `working/screwworm-content-guidelines.md`. NWS breeds on **live animals** — not feces. No veterinary treatment authority.

**Target:** **40–80** screwworm-adjacent terms → 2–3 posts/mo **unique vs Boar Blanket & Big Pig**.

### B5 — Commercial / Buy Now cluster

```
hogeye camera buy
hog trap camera system
cellular hog trap trigger
remote hog trap camera
ranch surveillance camera solar
off grid ranch camera
hogeye mini camera
```

**SF/GSC targets:** `/buy-now/` (241 GSC clicks, 22 words, no H1), `/steel-camera/`, `/net-camera-trap-remote-hog-trapping/`.

**Estimated Phase B tasks:** ~25–40 | **Cost:** Medium

---

## Phase C — SERP organic (intent validation)

**Goal:** Top **80–120** keywords by (GSC impressions × strategic weight).

| Batch | Count | Source |
| ----- | ----: | ------ |
| **C1 — Trap/camera core** | 15 | GSC strikers |
| **C2 — Comparison** | 12 | B2 |
| **C3 — Texas** | 15 | B3 |
| **C4 — LA/OK/MS/AL** | 20 | B3 |
| **C5 — Screwworm** | 12 | B4 |
| **C6 — Commercial/Buy Now** | 10 | B5 |
| **C7 — Refresh targets** | 8 | Low-CTR URLs (`trap-camera`, `steel-camera`, `blog-4g-vs-5g`, `/blog/`) |

**Per-SERP:** top 10 domains, SERP features, whether `hogeyecameras.com` ranks, competitor frequency (Vosker, Reolink, Spartan, Tractor Supply, extension .gov/.edu).

**Estimated tasks:** ~80–120 | **Cost:** Medium–high

---

## Phase D — LLM visibility

| # | Endpoint | Queries |
| - | -------- | ------- |
| D1 | `ai_optimization/llm_mentions/search/live` | Brand + category queries from `niche_config.yaml` llm_queries |
| D2 | `ai_optimization/chat_gpt/llm_scraper/live` | Top 15 commercial + 10 screwworm prompts |

**Sample ChatGPT prompts:**

- Best cellular camera for hog trapping
- HogEye vs Vosker for ranch monitoring
- What is screwworm and how do feral hogs spread it
- Remote hog trap trigger systems

**Estimated tasks:** ~20–30 | **Cost:** Medium

---

## Phase E — On-page, backlinks, business data

| # | Endpoint | URLs / targets |
| - | -------- | -------------- |
| E1 | `on_page/instant_pages` | `/`, `/buy-now/`, `/steel-camera/`, `/net-camera-trap-remote-hog-trapping/`, top 3 GSC blog URLs |
| E2 | `backlinks/summary/live` | hogeyecameras.com |
| E3 | `business_data/my_business_info` | HogEye brand query (US) |

**Estimated tasks:** ~8–12 | **Cost:** Low

---

## Phase F — Synthesis (required before calendar)

**Output:** `outputs/dataforseo-research-summary.md` (after run) feeding:

1. **`outputs/content-strategy-opportunities.md`** — refresh vs net-new matrix
2. **Content calendar** — **blocked until Phase F complete**
3. **Blog briefs** — screwworm queue coordinated via `clients/wildlife-dominion/working/screwworm-topic-matrix.md`

### Scoring dimensions (for prioritization)

| Dimension | Weight | Source |
| --------- | ------ | ------ |
| GSC impressions / striker status | High | GSC |
| Search volume + KD | High | DataForSEO Labs |
| SERP competitiveness | Medium | Phase C |
| LLM citation gap | Medium | Phase D |
| SF technical debt on URL | Medium | SF |
| Buy Now / conversion proximity | High | GA4 + SF |
| Screwworm stakeholder priority | High | Brief (greenfield) |
| Geo ad-weight (TX, MS, LA, OK, AL) | Medium | Brief |

---

## Cost estimate (order of magnitude)

| Phase | Tasks | Relative cost |
| ----- | ----: | ------------- |
| A — Labs footprint | 5–8 | $ |
| B — Keyword expansion | 25–40 | $$ |
| C — SERP advanced | 80–120 | $$$ |
| D — LLM | 20–30 | $$ |
| E — On-page/backlinks | 8–12 | $ |
| **Total** | **~140–210** | **Extensive (approved budget)** |

---

## Pre-flight checklist

- [x] SF crawl archived (`2026.06.22.agt-cursor`)
- [x] GSC pull refreshed (2026-06-22)
- [x] GA4 pull refreshed (2026-06-22)
- [x] GSC + GA4 findings docs written
- [ ] Stakeholder approval of this plan + budget
- [ ] Update `niche_config.yaml` seeds from Phase B lists above
- [ ] `dataforseo_niche_bundle.py --client hogeye --dry-run`
- [ ] Execute full run → Phase F synthesis → **then** calendar

---

## Do not do yet

- Content calendar or blog briefs
- Screwworm publish queue (except standby microsite if Schell triggers)
- DataForSEO API calls without approval
