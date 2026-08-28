# Keyword & SERP validation — DataForSEO (HogEye Cameras)

**Client:** HogEye Cameras (`hogeye`)  
**Document:** Keyword & market validation  
**Created:** 2026-04-09  

**Purpose:** Map **US** English demand and **SERP composition** for **wild/feral hog, trap, ranch, and cellular trail** themes when **Google Search Console queries are unavailable** — using a **niche-gated** Labs + Ads + SERP + LLM + domain bundle (not a generic “security camera” seed list).

**Primary data file:** [`clients/hogeye/inputs/dataforseo/dataforseo_hogeye_raw.json`](../inputs/dataforseo/dataforseo_hogeye_raw.json)

**Approximate total API cost:** **~$2.45** — field `approx_total_cost_usd` in the bundle.

**Strategy (bundle `meta`):** `niche_wild_feral_hog_trail_ranch` — keywords merged into Ads and SERP must pass **niche allow/deny** rules; **SERP query order** is **`strict_hog_intent_first_then_cellular_trail`** so live pulls prioritize hog/trap/ranch intent before broader trail/solar accessory terms.

---

## What was called (pipeline)

| Layer | Endpoint (summary) | Role |
| ----- | ------------------ | ---- |
| Labs | `POST /v3/dataforseo_labs/google/ranked_keywords/live` | Keywords **hogeyecameras.com** + **Vosker, Reolink, Spartan, barnowltech.com** rank for (organic); competitor rows **filtered by niche** |
| Labs | `POST /v3/dataforseo_labs/google/keyword_suggestions/live` | Long-tail seeds (hog / wild / trail / ranch phrasing) |
| Labs | `POST /v3/dataforseo_labs/google/related_keywords/live` | **Depth 3** on niche seeds |
| Keywords Data | `POST /v3/keywords_data/google_ads/search_volume/live` | Google Ads volume/CPC for merged niche keyword set |
| SERP | `POST /v3/serp/google/organic/live/advanced` | **55** live organic SERPs (**depth 10**), ordered **hog-first** then cellular/trail/solar tail |
| AI Optimization | `POST /v3/ai_optimization/llm_mentions/search/live` | **14** research-style LLM mention pulls |
| AI Optimization | `POST /v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` | **7** ChatGPT scraper tasks (`force_web_search`), niche prompts + `research_angle` text |
| Backlinks | `POST /v3/backlinks/backlinks/live` | Backlink rows per domain (client + competitors) |
| On-Page | `POST /v3/on_page/instant_pages` | Instant page analysis for **5** priority URLs |
| Business Data | `POST /v3/business_data/google/my_business_info/live` | Google Business Profile lookup (**HogEye Cameras**, US) |
| Labs | `POST /v3/dataforseo_labs/google/historical_rank_overview/live` | Monthly organic footprint — **hogeyecameras.com**, **vosker.com**, **reolink.com** |

**Merged keyword count (post niche gate):** **280** — `merged_unique_keywords_after_niche_gate`.

---

## Seeds (keyword_suggestions + related_keywords)

Representative API seeds align with **wild hog monitoring**, **feral hog trap**, **cellular trail for hogs**, **ranch / off-grid**, and **brand-adjacent** comparisons — see `KEYWORD_SUGGESTION_SEEDS` and `RELATED_SEEDS` in `analysis/_dataforseo_hogeye_run.py` for the exact strings.

---

## HogEye domain — Labs ranked keywords (sample)

Highest **Labs `keyword_info.search_volume`** examples for **`hogeyecameras.com`** in this run:

| Keyword (Labs) | Search volume (Labs) |
| -------------- | -------------------: |
| traps for wild pigs | 6600 |
| camera portal | 1300 |
| hogeye | 880 |
| cameras and parts | 880 |
| jager pro hog trapping | 390 |
| hog-eye / hog eye / hog camera / hog cam | 390 each (separate rows) |
| hogeye camera | 140 |

**Source:** `ranked_keywords` → HogEye block → `response.tasks[0].result[0].items` in the bundle.

**Takeaway:** Strong **brand and hog-trap** lexical variants; **“traps for wild pigs”** is a **head** informational term — pair with **product/trap-camera** landing alignment if you pursue it.

---

## SERP sample (55 queries, hog-first order)

**Summary:** **`hogeyecameras.com` appears in the top ~10 organic domains for 2 of 55** summarized SERPs (`serp_summaries` → `our_domain_in_organic_top`: **true** for **`hog camera`** and **`remote hog trap trigger`**). **AI Overview**–style blocks appeared in **4** of **55** pulls (`ai_overview_present`).

**Early queries (hog / trap intent — illustrative):**

| Query | AI overview | HogEye in top ~10 organic? | Sample organic domains (API order) |
| ----- | ------------- | -------------------------- | ----------------------------------- |
| traps for wild pigs | Yes | No | wildpiginfo.msstate.edu, pigbrig.com, gamechangertraps.com, feralhogs.tamu.edu, farmranchstore.com |
| hog camera | No | **Yes** | **hogeyecameras.com**, jagerpro.com, gamechangertraps.com, bigpigtrap.com, shop.wildlifedominion.com |
| remote hog trap trigger | No | **Yes** | amazon.com, hogtraptrigger.com, facebook.com, hoggbossgates.com, feralhogs.tamu.edu, **hogeyecameras.com** |

**Tail queries (broader trail/solar accessories — positions ~41–55 in this run):** e.g. **vosker camera**, **trail camera solar panel**, **game camera mounts** — dominated by **marketplaces**, **trailcampro.com**, **brand DTC**, and **forums**; **HogEye not** in the top organic set for those snapshots.

**Source:** `serp_summaries` in `dataforseo_hogeye_raw.json`.

**Takeaway:** Visibility is **strongest on explicit hog / remote-trigger** phrasing; **generic trail/solar** SERPs remain **crowded** — differentiation stays on **hog workflows, comparisons, and proof**.

---

## LLM mentions (14 sampled)

| Query | `hogeyecameras.com` in cited sources (summary flag) | Sample cited domains (API) |
| ----- | --------------------------------------------------- | --------------------------- |
| wild hog monitoring camera system | **Yes** | camerahogsllc.com, **hogeyecameras.com**, jagerpro.com, farmsteadoutdoors.com, opticsplanet.com |
| feral hog trap camera with cellular | No | youtube.com, feralhogs.tamu.edu, georgiawildlife.com, pigbrig.com, tpwd.texas.gov, jagerpro.com, … |

**Source:** `llm_summaries` in the bundle.

**Takeaway:** In this pass, **one** niche-system query cited the domain; many other prompts returned **.gov / .edu / extension** or **zero** mention rows — invest in **citable** specs and **clear differentiation** on owned pages.

---

## ChatGPT LLM scraper (7 tasks)

Research-style **keywords** plus **`research_angle`** text (examples): wild-hog monitoring checklist (US South), feral-hog removal / alerts, wild-hog vs home security rural LTE, **Vosker vs Reolink Go** trap decision criteria (2026), blog topic ideas, E-E-A-T for ranch/invasive-species content, **AI Overview citation patterns** for cellular trail. Full text and responses: `chatgpt_research` in the JSON.

---

## Backlinks (domain rows, API `total_count`)

| Domain | Backlink rows reported (`total_count`) |
| ------ | -------------------------------------: |
| hogeyecameras.com | 83 |
| vosker.com | 5,005 |
| reolink.com | 103,032 |
| spartancamera.com | 1,489 |
| barnowltech.com | 0 |

**Source:** `backlinks` array in the bundle (50 sample rows returned per non-empty domain).

**Takeaway:** HogEye’s **link scale** is **orders of magnitude smaller** than large consumer camera brands — **earned links** from **trapping, ag, and regional** contexts matter more than raw volume parity.

---

## On-Page instant (DataForSEO `on_page_instant`)

Approximate **`onpage_score`** from instant analysis: homepage **~96.3**, **/buy-now/** **~93.4**, **/hog-traps/** **~94.5**, **/blog/** **~90.5**; comparison URL block did not surface a single score in the same extraction path — see raw `on_page_instant` for full checks (e.g. HTML validation flags on **/blog/**).

---

## Historical rank overview (Labs — latest month in bundle: 2026-03)

Organic **ETV** and **keyword count** (Labs metrics, **not** GSC):

| Domain | Organic ETV (approx.) | Organic keyword count |
| ------ | --------------------: | --------------------: |
| hogeyecameras.com | ~569 | ~50 |
| vosker.com | ~14,778 | ~1,406 |
| reolink.com | ~956,197 | ~133,222 |

**Source:** `historical_rank_overview` → sort `items` by year/month; read latest month’s `metrics.organic`.

---

## Google Business Profile (`business_google`)

**`my_business_info/live`** for **“HogEye Cameras”** (US) returned **no items** (`status_message`: **No Search Results.**) — confirm **exact business name**, **address**, or **Maps category** for a repeat lookup if local pack matters.

---

## Content priorities (evidence-led)

1. **Fix broken URLs and HTTPS issues** (`outputs/technical-findings.md`) so traffic does not hit **404** or mixed content.  
2. **Strengthen category hubs** (meta + body) for **feral hog**, **cellular security**, **off-grid** — crawl flagged **missing meta descriptions** on some hubs.  
3. **Comparison / trap / remote-trigger** pages — align with **SERP** winners (hog + trigger queries) and **ChatGPT** research angles (carrier, solar, trap workflow).  
4. **FAQ / structured** copy where **AI Overviews** appear — answer **trap biology**, **remote trigger**, and **cellular** questions with **first-party** specs.

---

## Limitations

- **Ads search volume** is a **demand proxy**, not organic rank potential.  
- **SERP** and **LLM** snapshots are **one-time**; rankings change.  
- **`merged_unique_keywords_after_niche_gate`** still reflects **Labs expansion** — prioritize **`serp_queries_chosen`**, **HogEye ranked keywords**, and **stakeholder intent** over raw volume alone.
