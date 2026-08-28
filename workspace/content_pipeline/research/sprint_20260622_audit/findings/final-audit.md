# SEO & LLM visibility audit — HogEye Cameras

**Client:** HogEye Cameras (`hogeye`)  
**Document:** Final SEO & LLM visibility audit  
**Created:** 2026-04-09  

**Scope:** Production site **`https://hogeyecameras.com/`** per `client_config.yaml`. Staging excluded except where noted in intake.  
**Evidence:** Screaming Frog crawl (`inputs/screaming_frog/2026.04.09.05.15.26/`), GA4 CSVs (`inputs/ga/`), DataForSEO bundle (`inputs/dataforseo/dataforseo_hogeye_raw.json`).  
**Gap:** **Google Search Console** not available — **no query-level** performance from Google.

---

## Executive Summary

HogEye operates in a **highly competitive** US market for **cellular trail and ranch/hog-monitoring cameras**, where **organic SERPs** for **broad** trail and solar-accessory terms are dominated by **established hardware brands**, **marketplaces**, and **publishers**. The **latest DataForSEO bundle** uses a **niche-first** keyword merge and **hog/trap-heavy SERP ordering**: **`hogeyecameras.com` appeared in the top ~10 organic results for 2 of 55** sampled queries (**`hog camera`**, **`remote hog trap trigger`**), while **Labs** still shows meaningful **brand and hog-trap**-related queries for the domain. **LLM mention** samples cited **`hogeyecameras.com`** for **`wild hog monitoring camera system`** in this run; **ChatGPT LLM scraper** tasks (7) add **research narrative** on **Vosker vs Reolink**, checklists, and citation dynamics.

On-site, the crawl found **critical hygiene issues**: **four** **404** HTML URLs, **mixed content** and **HTTP** references on **19** URLs each, **missing meta descriptions** on **three** category hubs, and **thin** templates on key conversion and category paths. **GA4** shows **strong engagement on Organic Search** relative to other large channels and **material sessions** on **Buy Now**, **trap**, and **product** paths — **paid media** drives more **raw sessions** than organic in the sampled window.

The **next phase** should pair **technical fixes** (404s, HTTPS, snippets) with **differentiated content** (hog/ranch/trap workflows, comparisons, FAQs) that matches **how buyers actually search** and how **SERP and AI surfaces** already cite competitors and institutions.

---

## What this means for HogEye

- **Visibility gap on head terms** is **expected** at this stage — the opportunity is **niche authority** and **conversion clarity**, not generic “best camera” alone.  
- **Organic channel quality** (engagement rate in GA) supports **investing in SEO** once **crawl errors** and **HTTPS** are clean.  
- **Brand** appears in **LLM citation** samples for some queries — reinforce **citable facts** (specs, use cases, compliance) on owned pages.

---

## Competitive landscape (search)

Named competitors: **Vosker**, **Reolink**, **Barn Owl / RangeCam**, **Spartan**. Live SERPs repeatedly show **Stealth Cam**, **Spartan**, **Wildgame**, **Moultrie**, **Arlo**, **Reolink**, **Vosker**, **Amazon**, and **outdoor publishers**. Detail: `outputs/competitive-landscape.md`.

---

## Technical & on-page findings (crawl)

Summarized from `outputs/technical-findings.md`:

| Theme | Severity |
| ----- | -------- |
| **404** on **4** HTML URLs | High |
| **Mixed content** + **HTTP** URL issues (**19** URLs each) | High |
| **Missing meta descriptions** on **3** category hubs | High |
| **Thin content** flags on **Buy Now**, **Privacy**, **login**, **category** hubs | Medium |
| **H1** issues / duplicates per Screaming Frog (**12** missing in H1 export; **7** duplicate H1s) | Medium–High (validate DOM) |
| Short **titles** on **4** URLs | Medium |
| **PageSpeed** / image / CSS opportunities (broad) | Medium |

---

## Search performance (GA4)

Summarized from `outputs/search-opportunities.md`:

- **Organic Search:** **2631** sessions (**0.633** engagement rate) in **2026-01-09–2026-04-08**.  
- **Paid Social** and **Paid Search** exceed organic in **session volume** in this window — **organic** still **material**.  
- **Landing:** Homepage and **Buy Now** dominate; **comparison** URL receives fewer sessions but strong key-event rate in export.

---

## Market & SERP findings (DataForSEO)

Summarized from `outputs/keyword-opportunities.md`:

- **55** live SERPs sampled (**hog/trap intent first**, then broader trail/solar tail); **AI Overview**–style blocks on **4**; **`hogeyecameras.com` in top ~10 organic for 2** queries (**`hog camera`**, **`remote hog trap trigger`**).  
- **~280** niche-gated merged keywords; **Labs** shows **brand** and **hog**-related queries for **`hogeyecameras.com`**; **“traps for wild pigs”** remains a **high-volume** Labs head term — treat as **strategic** (content + intent fit), not automatic priority.  
- **LLM mentions:** **`wild hog monitoring camera system`** cites **`hogeyecameras.com`** in this sample; **backlinks** and **historical_rank_overview** quantify the **gap vs large brands** (see keyword doc).  
- **Google Business Profile** API lookup returned **no rows** — verify business name/address for local relevance.  
- **Approx. bundle cost** **~$2.45** (`approx_total_cost_usd`).

---

## Strategic recommendations

1. **Fix 404s and HTTPS** — Update or redirect **`/resources`**, **`trap-camera/`**, **`sim-card-performance…`**, **`reolink-trap-mods…`**; enforce **HTTPS** and remove **mixed content**.  
2. **Category hubs** — Add **unique meta descriptions** and **intro copy** for **feral hog**, **cellular security**, and **off-grid** category pages.  
3. **Titles & H1** — One **clear H1** per template; expand **short titles** on commercial pages where appropriate.  
4. **Comparison & education** — Support **GA**-visible **comparison** and **trap** pages with **internal links** from blog and category content; align with **SERP** competitors (publishers + brands).  
5. **AI-ready answers** — Add **FAQ** and **spec** blocks for **carrier**, **power**, **mount**, and **trap integration** questions — categories where **AI Overviews** appeared for cellular trail queries.  
6. **Measurement** — Add **Google Search Console** when available; reconcile **GA4** key events with **Buy Now** UX (ecommerce vs quote).

---

## Freebies (quick wins)

- **Meta descriptions** for the **three** category URLs currently missing them (exact paths in `technical-findings.md`).  
- **Internal link audit** from blog posts to **`/buy-now`** and **top product** URLs using **descriptive anchor text** (Screaming Frog flags **missing anchor text** broadly).  
- **Single source of truth** for **`/resources`** — pick **HTTPS** + **www/non-www** canonical and redirect **HTTP** host.

---

## Limitations & unknowns

- **No GSC** — cannot rank by queries, impressions, or CTR.  
- **SERP** and **LLM** samples are **snapshots** — not continuous rank tracking.  
- **Barn Owl** Labs domain (**barnowltech.com**) should be **verified** against the live brand site.  
- **Moderate trust** topics (`client_config.yaml`) — keep **disease** / **livestock** framing **educational**, not diagnostic.

---

## Final note

HogEye’s **next SEO lift** is **foundational**: remove **errors** and **mixed content**, strengthen **category and conversion** templates, and **differentiate** on **hog and ranch** use cases where **generic** camera SERPs are crowded. When **Search Console** is connected, **refresh** this audit with **query–URL** evidence — not a replacement for the competitive reality already visible in **SERP** and **GA4** samples here.
