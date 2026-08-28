# Search performance & opportunities — HogEye Cameras

**Client:** HogEye Cameras (`hogeye`)  
**Document:** Search performance & opportunities  
**Created:** 2026-04-09  

**Evidence:** Google Analytics 4 CSV exports in `clients/hogeye/inputs/ga/`.  
**Gap:** **Google Search Console** is not available — **no query, impression, CTR, or average position** data from Google. Organic performance is inferred from **channel + landing-page** reports only.

---

## Reporting windows

| Export | Date range | Role |
| ------ | ---------- | ---- |
| `Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group) (1).csv` | 2026-01-09 to 2026-04-08 | Channel mix (all users) |
| `Landing_page_Landing_page.csv` | 2026-01-09 to 2026-04-08 | Landing-page sessions and key events |
| `Events_Event_name.csv` | 2026-01-09 to 2026-04-08 | Event mix |

Property: **hogeye-wdm** (account **wildlifedominion**) per file headers.

---

## Channel mix (all users, 2026-01-09–2026-04-08)

| Session primary channel group | Sessions | Engaged sessions | Engagement rate |
| ----------------------------- | -------: | ---------------: | ----------------: |
| Paid Social | 3998 | 283 | 0.071 |
| Paid Search | 3608 | 2036 | 0.564 |
| Direct | 2732 | 1322 | 0.484 |
| **Organic Search** | **2631** | **1665** | **0.633** |
| Display | 1015 | 18 | 0.018 |
| Unassigned | 558 | 92 | 0.165 |
| Other | smaller | — | — |

**Source:** `Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group) (1).csv` (comment block lines 8–9; data rows 11+).

### Takeaways

- **Paid media** (Paid Social + Paid Search + Display) accounts for the **largest share of sessions** in this window — organic is **material** (2631 sessions) but **not the majority** of attributed sessions here.
- **Organic Search** shows the **highest engagement rate** among large channels in this export (**0.633**) — consistent with intent-driven traffic when it reaches the site.
- **Display** engagement is **very low** in this snapshot (0.018) — worth validating creative/landing alignment in Ads platforms (outside this repo).

---

## Landing pages (all users, same window)

| Landing page (path) | Sessions | Session key event rate | Notes |
| --------------------- | -------: | ---------------------: | ----- |
| `/` | 11059 | 0.998 | Homepage — largest entry |
| `(not set)` | 944 | 0.798 | Tagging / unassigned landing |
| `/buy-now` | 542 | 0.996 | Primary commercial path |
| `/camera-login` | 390 | 1.0 | Product/account |
| `/camera-resources` | 165 | 1.0 | Support content |
| `/buy-now-legacy` | 146 | 0.993 | Legacy path |
| `/steel-camera` | 145 | 1.0 | Product |
| `/products/big-pig-drop-trap` | 144 | 1.0 | Product |
| `/hog-traps` | 134 | 0.993 | Commercial/education |
| `/reolink-vs-vosker-vs-hogeye-off-grid-camera-comparison` | 28 | 1.0 | Comparison content |

**Source:** `Landing_page_Landing_page.csv` (top rows; full file has additional paths).

### Takeaways

- **Homepage** dominates **landing** sessions; **Buy Now** and **trap/product** URLs are meaningful conversion surfaces.
- **Comparison** URL (`/reolink-vs-vosker-vs-hogeye-off-grid-camera-comparison`) has lower volume but **full session key event rate** in this export — supports investing in **comparison and category** content tied to Buy Now (see `keyword-opportunities.md`).

---

## Conversion-related events (same window)

| Event name | Event count | Total revenue (USD) |
| ---------- | ----------: | --------------------: |
| page_view | 21438 | 0 |
| view_item | 896 | 0 |
| begin_checkout | 166 | 0 |
| purchase | 117 | **68478** |
| add_to_cart | 34 | 0 |

**Source:** `Events_Event_name.csv`.

### Takeaways

- **Purchase** revenue is aggregated in GA4 export — use for **directional** funnel health, not as a substitute for finance reconciliation.
- **View_item** / **begin_checkout** / **purchase** volumes support **ecommerce-style** tracking; align SEO landing pages with **product** and **Buy Now** journeys.

---

## What we cannot see (no GSC)

- Which **queries** drive organic sessions  
- **Impressions / CTR / position** per page or query  
- **Index coverage** or **manual actions** from Google  

**Next step when GSC exists:** Upload `Pages` / `Queries` to `inputs/gsc/` and re-rank content and technical fixes by **query–URL** performance.

---

## Cross-reference

- **Demand & SERP shape:** `outputs/keyword-opportunities.md` and `outputs/competitive-landscape.md` (DataForSEO).  
- **Technical barriers:** `outputs/technical-findings.md` (404s, HTTPS, snippets).  
