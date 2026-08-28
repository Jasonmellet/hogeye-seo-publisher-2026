# GA4 findings — HogEye Cameras

**Client:** HogEye (`hogeye`)  
**Document:** GA4 findings (lightweight)  
**Created:** 2026-06-22  

## How to read this document

- **Scope:** GA4 property **`245859533`** (`hogeyecameras.com`).
- **Sources:** `clients/hogeye/inputs/ga/Traffic_acquisition_Session_primary_channel_group_by_month.csv`, `Landing_page_Landing_page.csv` (API pull via `analysis/google_wildlife_dominion_pull.py --brand hogeye`, fetched **2026-06-22**).
- **Date range:** **2024-01-01** to **2026-06-21** (per pull script `--start-date`).
- **Evidence rule:** All numbers from these CSVs. **Landing page export is not segmented by channel** — page tables are **all-channel** unless noted.

### Older manual exports

Prior manual GA4 CSVs (Jan–Apr 2026 window, event-level detail) remain under `inputs/ga/` with `Events_Event_name.csv` etc. This document uses the **API pull** as primary for channel mix and landing volume. Event-level funnel analysis was not re-pulled in this run.

---

## Executive summary

HogEye traffic is **multi-channel**, not organic-only: **Direct (36.4%)** and **Organic Search (25.2%)** lead, with **Organic Social (16.6%)** and **Paid Search (10.1%)** significant.

**Revenue** (**~$152k** summed in channel file, Dec 2025–Jun 2026 months) concentrates on **Direct** and **Unassigned** — **Organic Search revenue is only ~$753** in the export, indicating **SEO content is not the primary commerce driver today** despite healthy organic **sessions**.

**Buy Now** (`/buy-now`) records **1,144** landing sessions (all channels) but **$0** attributed revenue in the landing export — validate purchase event + revenue tagging on conversion paths.

---

## Traffic overview (channel file, summed)

| Channel | Sessions | Share | Total revenue |
| ------- | -------: | ----: | ------------: |
| **Direct** | **55,233** | **36.4%** | **$90,522** |
| **Organic Search** | **38,226** | **25.2%** | **$753** |
| **Organic Social** | **25,137** | **16.6%** | $0 |
| **Paid Search** | **15,359** | **10.1%** | $0 |
| **Paid Social** | **7,117** | **4.7%** | $0 |
| **Unassigned** | **5,080** | **3.4%** | **$41,571** |
| **Display** | **2,722** | **1.8%** | $0 |
| **Organic Shopping** | **90** | **0.1%** | **$19,805** |
| **All channels** | **151,574** | 100% | **~$152,651** |

**Interpretation:** Organic search drives **volume** but **minimal attributed revenue** in GA4. Content SEO success should be measured with **GSC** (clicks, non-brand growth) until ecommerce/revenue tagging on `/buy-now` is verified.

---

## Organic Search trend (by month)

Recent **Organic Search** sessions (`yearMonth`):

| Month | Organic Search sessions |
| ----- | ----------------------: |
| 202508 | 827 |
| 202509 | 944 |
| 202510 | 706 |
| 202512 | 978 |
| 202601 | 974 |
| 202602 | 1,005 |
| 202603 | 787 |
| 202604 | 683 |
| 202605 | 643 |
| 202606 | 447 |

**Pattern:** Roughly **600–1,000** organic search sessions/month in late 2025 through early 2026, **softening** in May–Jun 2026. Do not over-interpret without confirming tracking/consent changes in GA4 Admin.

---

## Landing page performance (all channels)

**687** landing paths; **149,239** summed sessions.

| Landing page | Sessions | Total revenue |
| ------------ | -------: | ------------: |
| `(not set)` | 53,027 | $0 |
| `/` | 50,006 | $150 |
| `/farm-ranch` | 28,709 | $0 |
| `/shop` | 4,312 | $0 |
| `/camera-login` | 2,040 | $0 |
| `/payment-options` | 1,435 | $0 |
| `/trap-camera` | 1,188 | $0 |
| **`/buy-now`** | **1,144** | **$0** |
| `/camera-resources` | 396 | $0 |
| `/steel-camera` | 329 | $0 |
| `/hog-traps` | 300 | $0 |

**Commercial paths** (`/buy-now`, `/shop`, `/trap-camera`, product pages) receive meaningful sessions but **little or no revenue** in this dimension — flag for **GTM/GA4 ecommerce audit**.

---

## Blog / content landings (all channels)

| Landing page | Sessions |
| ------------ | -------: |
| `/blog` | 39 |
| `/blog-4g-vs-5g-cellular-cameras-ranch-monitoring-2025` | 36 |
| `/blog-ultimate-guide-setting-up-hogeye-camera-trap` | 25 |
| `/blog-how-to-spot-feral-hog-damage` | 19 |
| `/net-camera-trap-remote-hog-trapping` | 112 |

Blog URLs are **small** as GA4 entry points vs homepage and `/farm-ranch`. GSC shows some posts with **high impressions** — users may land on homepage then navigate, or attribution differs by dimension.

**Cross-check GSC:** `/blog-4g-vs-5g-…` has **7,454** impressions but only **36** GA4 landing sessions — supports **title/meta CTR optimization** rather than low rank alone.

---

## Buy Now / conversion observations

| Signal | Value | Source |
| ------ | ----- | ------ |
| `/buy-now` landing sessions | **1,144** | `Landing_page_Landing_page.csv` |
| `/buy-now` landing revenue | **$0** | Same |
| GSC `/buy-now/` clicks | **241** | `outputs/gsc-findings.md` |
| SF word count on `/buy-now/` | **22** | `outputs/technical-findings.md` |

**Gap:** Strong **discovery** (GSC + sessions) but **weak on-page depth** (SF) and **no revenue attribution** on Buy Now in GA4 landing export. Technical + tracking fixes precede content scale on conversion URL.

---

## Revenue concentration (non-zero months)

Channel file shows revenue primarily from **202512–202606**:

| Month | Total revenue (all channels) |
| ----- | ---------------------------: |
| 202512 | $20,291 |
| 202601 | $20,814 |
| 202602 | $26,565 |
| 202603 | $17,662 |
| 202604 | $22,860 |
| 202605 | $24,795 |
| 202606 | $19,664 |

**Direct** + **Unassigned** dominate revenue attribution — not Organic Search.

---

## Implications for DataForSEO plan

1. **SEO KPIs:** Weight **GSC non-brand clicks/impressions** and **striker query coverage** over GA4 organic revenue (until tagging fixed).
2. **Content clusters:** Trap/camera monitoring, comparison, 4G/5G ranch — align with GSC strikers and existing blog URLs with high impressions.
3. **Screwworm:** No GA4 signal yet — greenfield.
4. **Geo:** `/farm-ranch` is a major landing page (**28,709** sessions) — validate overlap with TX/Southern campaign targeting in Phase B seeds.

---

## Sources

- Pull: `analysis/google_wildlife_dominion_pull.py --brand hogeye --start-date 2024-01-01`
- Summary: `clients/wildlife-dominion/working/google-pull-summary.json`
- GSC companion: `outputs/gsc-findings.md`
