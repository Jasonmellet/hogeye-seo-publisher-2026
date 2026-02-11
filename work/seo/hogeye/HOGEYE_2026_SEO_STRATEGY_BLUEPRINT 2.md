## Hogeye — 2026 SEO Strategy & Content Blueprint (Draft)

Prepared for client review • 2026-01-30 • Data-driven baseline in place • Planning horizon: **Jan–Jun 2026**

### Executive summary

Hogeye is early-stage (“fledgling”) but already has enough signal to build a **BB-level execution workflow**: baseline data → Month 1 plan (5 new + 5 updates) → briefs → local AI drafts → staged WordPress drafts (one at a time).
The biggest immediate constraint is **brand dependency**: the majority of current GSC clicks are branded. **Important nuance from the deep export:** non-brand query volume is still thin at meaningful scale (in the 365‑day non-brand query export, only one query clears ≥1,000 impressions). Month 1 should therefore prioritize:

- **Quick wins on pages already getting impressions** (CTR + striking-distance style improvements)
- **Non-brand expansion** into the trap + trigger + remote system ecosystem, using a head-term approach (high-demand topics where Hogeye does not rank yet)
- **Internal linking** that routes informational traffic into the commercial flows (shop/signup/product pages)

This document is the overview. The execution plan will be organized into:

- **Overview tab**
- **Jan–Jun tabs** (monthly allocations: new + updates + backlinks + technical)
- **Technical SEO month-by-month plan** (explicit fix list)

Primary roadmap document (source of truth for month-by-month planning):

- `work/seo/hogeye/HOGEYE_2026_SEO_6_MONTH_PLAN_FEB_JUN.md`

### Supporting artifacts (source of truth)

- **Runbook & tracking**: `work/seo/hogeye/` (`RUNBOOK.md`, `SAFETY_WORKFLOW.md`, `PROGRESS_TRACKER.md`, `EXECUTION_STATUS.md`)
- **GSC exports (local)**: `work/seo/gsc/`
- **Screaming Frog exports (local)**: `work/seo/screaming_frog/`
- **DataForSEO benchmark (local)**: `work/seo/benchmark/2026-01-26/`

---

## Baseline snapshot (Google Search Console)

**Data scope note (updated):** We now have two layers of GSC exports:

- **Benchmark sample exports** (quick, smaller): `work/seo/gsc/*_last_28d_v2/` and `work/seo/gsc/*_last_365d_v2/`
  - Top 50 pages sitewide
  - Top queries per page (up to 100/page)
- **Deep exports (preferred for planning)**: `work/seo/gsc_deep/`
  - Sitewide pages, sitewide queries, and sitewide page+query pairs
  - Split into **brand** vs **non-brand**

The GSC API itself returns “top rows” for a chosen dimension set (it does not guarantee every low-impression query). But for Hogeye, the deep export is effectively the “all necessary data” set for planning Month 1 and building a Jan–Jun roadmap.

### 365-day window (2025-01-29 → 2026-01-29)

Top 50 pages rollup:

- **Clicks**: 6,742
- **Impressions**: 208,805
- **CTR**: 3.23%
- **Avg position (impression-weighted)**: 7.87

Brand vs non-brand (queries-by-page sample):

- **Brand clicks**: 3,567 (97.7% of sample clicks)
- **Non-brand clicks**: 85 (2.3% of sample clicks)
- **Brand impressions share**: 76.6%

### 28-day window (2026-01-01 → 2026-01-29)

Top 50 pages rollup:

- **Clicks**: 480
- **Impressions**: 17,451
- **CTR**: 2.75%
- **Avg position (impression-weighted)**: 5.87

Brand vs non-brand (queries-by-page sample):

- **Brand clicks**: 186 (93.5% of sample clicks)
- **Non-brand clicks**: 13 (6.5% of sample clicks)
- **Brand impressions share**: 65.7%

### Immediate interpretation

- Hogeye is already showing **strong brand navigation demand** (camera login, signup, shop).
- The February growth lever is **CTR uplift on pages already earning impressions** while we begin building non-brand “head term” authority (new pages that earn impressions over 4–12 weeks).

---

## Technical snapshot (Screaming Frog crawl)

Source: `work/seo/screaming_frog/hogeye_screaming_frog_jan_2026_30th_spider.csv`

**Crawl coverage in this export (subset):**

- Rows in export: 94
- HTML pages: 11
- HTML status codes: 10×200, 1×404
- HTML indexability: 10 indexable, 1 non-indexable

**Metadata / structure gaps (HTML-only in this export):**

- Missing title tags: 1
- Missing meta descriptions: 1
- Missing H1 tags: 9

**Performance (lab)**

- Avg Performance Score across HTML pages in this export: ~55.7/100

### Immediate interpretation

- The “missing H1” count is the loudest on-page fix signal (even if some pages are builder/template driven).
- There is at least one clear **404** (`/resources`), which is a quick cleanup win.

---

## DataForSEO baseline (SERP + competitors + backlinks + on-page crawl)

Source: `work/seo/benchmark/2026-01-26/`

What we pulled:

- **SERP rank snapshot**: 60 keywords (`Benchmark_DataForSEO_RankSnapshot.csv`)
- **SERP top results**: 600 rows (60 keywords × top 10) (`Benchmark_SERP_TopResults.csv`)
- **SERP feature counts**: 14 feature types observed (`Benchmark_SERP_FeatureCounts.csv`)
- **SERP competitor domains**: 44 domains (`Benchmark_SERP_CompetitorDomains.csv`)
- **Backlinks gap**: 657 “gap” referring domains (`Benchmark_Backlinks_GapDomains.csv`)
- **Backlinks ref domains**:
  - Target sample: 43 domains
  - Competitors sample: 879 rows across competitor domains
- **OnPage crawl (DataForSEO)**: 10 pages crawled (`Benchmark_OnPage_Pages.csv`)

Notes:

- The OnPage crawl was intentionally conservative (cost control). Screaming Frog is the better technical “inventory” baseline.
- The DataForSEO keyword set used for SERP baselines was auto-derived (keywords-for-site). To consistently find **low/medium difficulty + high volume** opportunities, we should run a dedicated **keyword universe build** (camera + trap + triggers + remote systems) and then re-snapshot SERPs for those segments.

---

## Month 1 (5 new + 5 updates): how we’ll choose

We now have the ingredients to pick the Month 1 allocation without guessing:

- **Updates (5)** should come from:
  - high impressions pages (top 50 GSC) with low CTR
  - pages sitting around positions ~4–15 (striking distance behavior)
  - SF flags (missing H1/meta/title) on pages that already get traffic
- **New content (5)** should focus on high-demand topics where Hogeye is not ranking today:
  - “hog traps” / “hog traps for sale” / “hog traps near me”
  - trigger systems (cellular/remote door triggers)
  - remote hog trap systems (monitoring + decision + action)
  - trap camera pages remain important, but Month 1’s “new” priority is to build the head-term layer

### Month 1 (February) allocation (planning only)

This is the planned Month 1 set and will be executed only after you approve deliverables:

- **5 updates (GSC page-level CTR wins)**
  - `https://www.hogeyecameras.com/trap-camera`
  - `https://www.hogeyecameras.com/farm-ranch`
  - `https://www.hogeyecameras.com/resources` (404 fix + redirect/restore decision)
  - `https://www.hogeyecameras.com/net-trap`
  - `https://www.hogeyecameras.com/cameras`

- **5 new pieces (DataForSEO head-term gaps; Hogeye not ranking)**
  - Hog Traps — Complete Guide (Types, Sizes, When to Use Each)
  - Hog Traps for Sale — Where to Buy + Price Ranges (2026)
  - Hog Traps for Sale Near Me — How to Find Local Options
  - Hog Trap Trigger Systems — Cellular, Remote, and Door Triggers
  - Remote Hog Trap Systems — Monitoring + Triggering Workflow

### Execution constraints (must stay true)

- **No WordPress writes unless approved per piece** (draft-only when approved).
- **Drafts generated locally first** (brief → local AI draft → human review → WP draft one-at-a-time).
- **Updates require backup + diff + approval** before any WP write.

---

## Next steps (what I’ll produce next)

1) A Hogeye-specific **overview summary table** (top pages, top brand queries, top non-brand queries) to support Month 1 selection.
2) Maintain the February plan as the Month 1 source of truth: `work/seo/hogeye/HOGEYE_FEB_2026_SEO_PLAN.md`.
3) Use the 6‑month roadmap as the planning backbone: `work/seo/hogeye/HOGEYE_2026_SEO_6_MONTH_PLAN_FEB_JUN.md`.
4) Re-run a SERP snapshot after March to validate competitor movement and adjust April–June.
