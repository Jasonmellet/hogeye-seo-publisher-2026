# Search Console findings — HogEye Cameras

**Client:** HogEye (`hogeye`)  
**Document:** GSC findings (lightweight)  
**Created:** 2026-06-22  

## How to read this document

- **Scope:** Google Search Console property **`sc-domain:hogeyecameras.com`**.
- **Sources:** `clients/hogeye/inputs/gsc/Performance_by_date.csv`, `Pages.csv`, `Queries.csv` (API pull via `analysis/google_wildlife_dominion_pull.py --brand hogeye`, fetched **2026-06-22**).
- **Date range:** **2025-02-08** to **2026-06-20** (**498** days). No GSC rows before 2025-02-08 in this export.
- **Evidence rule:** All numbers from these CSVs. Position and CTR are **GSC averages** for the period — not live rank checks.

### Cross-dataset notes

- **Host duplication:** GSC reports clicks on both **`https://hogeyecameras.com/`** and **`https://www.hogeyecameras.com/`** (and parallel paths on `signup.`, `www.`). Canonical/www preference is still an open item in `client_config.yaml`.
- **`/trap-camera/`:** GSC shows **128** clicks on `https://www.hogeyecameras.com/trap-camera` (and related paths) but the Jun 2026 SF crawl returns **404** on `https://hogeyecameras.com/trap-camera/` — fix redirects and internal links urgently.
- **Screwworm:** **0** queries containing “screw” in the export — **greenfield** topic cluster for Phase 6 planning.

---

## Executive summary

Organic search is **dominated by brand demand**: **~49%** of query-level clicks come from brand terms (`hogeye`, `hog eye`, `hogeyecameras` variants). Sitewide CTR is **strong at 7.78%** (**8,522** clicks / **109,525** impressions) vs many content sites — but **non-brand capture is thin** (**137** clicks from queries without brand tokens that still earned clicks).

**Strengths:** Brand queries rank **positions 1–4**; homepage, **camera-login**, **buy-now**, and **camera-resources** earn meaningful clicks; comparison/how-to blog URLs appear in GSC with growing impressions.

**Gaps:** **956** of **1,013** query rows have **0 clicks**; high-impression commercial URLs (**trap-camera**, **steel-camera**, **hog-traps**, **shop**) have **low CTR**; **screwworm** and **state/geo** queries have little or no traction yet; **www vs apex** splits equity.

---

## Sitewide performance

| Metric | Value | Source |
| ------ | -----: | ------ |
| **Total clicks** | **8,522** | `Performance_by_date.csv` (sum) |
| **Total impressions** | **109,525** | `Performance_by_date.csv` (sum) |
| **Average CTR** | **7.78%** | clicks ÷ impressions |
| **Unique queries (export)** | **1,013** | `Queries.csv` row count |
| **Unique pages (export)** | **110** | `Pages.csv` row count |
| **Queries with 0 clicks** | **956** | **94.4%** of query rows |

---

## Brand vs non-brand demand

Brand classification: query contains **`hogeye`**, **`hog eye`**, **`hog-eye`**, or **`hogeyecameras`**.

| Segment | Clicks | Share of query-row clicks |
| ------- | -----: | ------------------------- |
| **Brand queries** | **4,171** | **~49%** |
| **Non-brand (with clicks > 0)** | **137** | **~1.6%** |
| **All other query rows** | **0 clicks** | Impression-only long tail |

**Top brand queries:**

| Query | Clicks | Impressions | Avg position |
| ----- | -----: | ----------: | -----------: |
| hogeye camera | 1,076 | 2,146 | 1.3 |
| hogeye | 842 | 11,450 | 3.4 |
| hog eye camera | 668 | 1,383 | 1.2 |
| hogeye camera system | 381 | 896 | 1.4 |
| hog eye | 321 | 4,519 | 3.7 |
| hogeye traps | 234 | 915 | 1.9 |
| hog eye trap | 230 | 950 | 2.6 |

**Top non-brand queries (with clicks):**

| Query | Clicks | Impressions | Avg position |
| ----- | -----: | ----------: | -----------: |
| camera login | 35 | 1,538 | 9.6 |
| hog camera | 15 | 314 | 2.8 |
| wildlife dominion | 9 | 617 | 5.9 |
| hog cam | 5 | 2,035 | 7.6 |
| vosker vs reolink | 3 | 41 | 2.4 |
| hog trap remote trigger | 2 | 73 | 9.1 |

**Interpretation:** Brand defense is excellent. Content sprint should expand **non-brand trap/camera/monitoring** capture and **comparison** queries without diluting login/support intent already earning clicks.

---

## Top pages by clicks

| Page (normalized path) | Clicks | Impressions | CTR | Avg position |
| ---------------------- | -----: | ----------: | ---: | -----------: |
| `/` (incl. www host rows) | **5,389+** | **~68k** | ~7–9% | ~4–14 |
| `signup.hogeyecameras.com/` | 1,006 | 21,554 | 4.67% | 3.9 |
| `/camera-login/` | 653+ | **~27k** | ~2–3% | ~4–6 |
| `/buy-now/` | 241 | 9,404 | 2.56% | 4.2 |
| `/camera-resources/` | 167 | 11,078 | 1.51% | 4.0 |
| `/hog-traps/` | 159 | 12,825 | 1.24% | 5.9 |
| **`/trap-camera/`** (404 in SF) | **128+** | **~17k** | **0.74%** | 8.6 |
| `/steel-camera/` | 62 | 10,558 | 0.59% | 4.4 |
| `/net-camera-trap-remote-hog-trapping/` | 56 | 4,317 | 1.30% | 9.4 |

**Pattern:** **Support/login** and **brand homepage** win clicks. **Commercial/product** URLs get **high impressions, low CTR** — title/meta and on-page depth (see SF `technical-findings.md`) likely suppress clicks.

---

## Striker queries (0 clicks, impressions ≥ 50, position 4–15)

**26** queries in this band — priority for content refresh or new posts:

| Query | Impressions | Avg position |
| ----- | ----------: | -----------: |
| camera hog | 654 | 6.3 |
| hog view | 606 | 8.4 |
| hog cams | 408 | 9.2 |
| wild hog trap monitoring | 239 | 5.5 |
| best camera for hog trapping | 206 | 11.6 |
| smart hog trap technology | 206 | 9.2 |
| hog control system | 191 | 6.6 |
| drop trap camera system | 213 | 9.3 |

Use these to seed **DataForSEO Phase B** (see `outputs/dataforseo-research-plan.md`).

---

## Comparison & competitor queries

| Query | Clicks | Impressions | Position |
| ----- | -----: | ----------: | -------: |
| hogeye vs boarbuster | 0 | 185 | 10.0 |
| vosker vs reolink | 3 | 41 | 2.4 |
| cellular hog traps for sale | 0 | 207 | 34.0 |
| 4g vs 5g trade-off for rural areas | 0 | 40 | 7.3 |

Existing blog URLs (e.g. `/blog-4g-vs-5g-cellular-cameras-ranch-monitoring-2025`, `/blog-hogeye-vs-vosker-cellular-cameras-comparison`) have impressions but **low CTR** — refresh candidates after DataForSEO SERP review.

---

## Geography (state queries)

Only **11** query rows mention priority states (TX, MS, LA, OK, AL, etc.); most have **0 clicks**:

| Query | Impressions | Clicks |
| ----- | ----------: | -----: |
| hog traps for sale in louisiana | 204 | 0 |
| hogeye arkansas | 7 | 0 |
| texas remote pig tracking | 6 | 0 |

**Stakeholder ad-weighting** (TX ~40%; MS/LA/OK/AL ~60%) is **not yet reflected in GSC demand** — geo content is a **net-new** opportunity, especially for screwworm series.

---

## Screwworm

| Metric | Value |
| ------ | ----- |
| Queries with “screw” in text | **0** |
| Impressions | **0** |

Greenfield cluster — no cannibalization risk. Plan via stakeholder brief + DataForSEO Labs expansion (Phase B in research plan).

---

## Content / blog performance (GSC)

| URL | Clicks | Impressions | CTR |
| --- | -----: | ----------: | --- |
| `/blog-4g-vs-5g-cellular-cameras-ranch-monitoring-2025` | 19 | 7,454 | 0.25% |
| `/blog-ultimate-guide-setting-up-hogeye-camera-trap` | 17 | 957 | 1.78% |
| `/blog-hogeye-vs-vosker-cellular-cameras-comparison` | 10 | 706 | 1.42% |
| `/hog-trapping-cameras-compared-2026-hogeye-vs-trail/` | 7 | 517 | 1.35% |
| `/blog/` (index) | 1 | 3,140 | 0.03% |

Blog index **3,140 impressions / 1 click** — aligns with SF placeholder meta on `/blog/`.

---

## Implications for DataForSEO plan (Phase 5)

1. **Prioritize non-brand strikers** and **comparison** clusters over more brand-defense content.
2. **Screwworm** — full Labs + SERP + LLM batch (no GSC baseline).
3. **Geo batch** — TX, MS, LA, OK, AL hog/camera/monitoring seeds (GSC barely present).
4. **URL refresh map** — high-impression / low-CTR URLs from this doc + SF 404 on `/trap-camera/`.
5. **Do not** build calendar until DataForSEO Phase 6 completes.

---

## Sources

- Pull: `analysis/google_wildlife_dominion_pull.py --brand hogeye --start-date 2024-01-01`
- Summary: `clients/wildlife-dominion/working/google-pull-summary.json`
