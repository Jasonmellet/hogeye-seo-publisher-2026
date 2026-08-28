# Competitive landscape (search) — HogEye Cameras

**Client:** HogEye Cameras (`hogeye`)  
**Document:** Competitive landscape (search)  
**Created:** 2026-04-09  

## What “competition” means here

**Named competitors** from `client_config.yaml`: **Vosker**, **Reolink**, **Barn Owl / RangeCam**, **Spartan**.  

**Search competitors** are the domains and page types that **actually appear in Google organic results** for priority queries. Evidence: **DataForSEO** live SERP snapshots (`/v3/serp/google/organic/live/advanced`), **Labs ranked_keywords**, **backlinks/live**, and **historical_rank_overview** — see [`clients/hogeye/inputs/dataforseo/dataforseo_hogeye_raw.json`](../inputs/dataforseo/dataforseo_hogeye_raw.json). **United States**, **English**.

**SERP ordering in this bundle:** Queries run **strict hog / trap / ranch intent first**, then **broader cellular trail / solar accessory** terms (`meta.serp_order`). The **first** SERP rows emphasize **traps, Jager-adjacent hog trapping, remote hog traps, and cellular hog trap gate**; **later** rows include **Vosker**, **solar trail accessories**, and **mounts**.

---

## Recurring organic competitor types (from 55 SERP samples)

**1. Trail camera incumbents & DTC brands**  
Examples in **tail** SERPs (solar, mounts, game camera): **moultrie.com**, **go.spartancamera.com**, **stealthcam.com**, **wildgameinnovations.com**, **tactacam.com**, **browningtrailcameras.com** (varies by query).

**2. Named stack competitors**  
- **Vosker** (**vosker.com**) appears on **brand** and **commercial** queries in the sample.  
- **Reolink** (**reolink.com**) — massive **historical** footprint vs HogEye in Labs historical data; competes on **broad cellular** demand.

**3. Hog-trap and equipment specialists**  
On **hog trap** and **remote trigger** queries: **gamechangertraps.com**, **pigbrig.com**, **hoggbossgates.com**, **jagerpro.com**, **hogtraptrigger.com**, **amazon.com**.

**4. Marketplaces & big-box**  
**amazon.com**, **tractorsupply.com**, **homedepot.com**, **walmart.com** on **commercial** and **product** intents.

**5. Publishers & community**  
**reddit.com**, **youtube.com**, **forums** — reviews and **UGC** on **gear** and **how-to** intents.

**6. Education / agency / extension**  
On **wild pig** and **feral hog** education intents: **.edu** and state agency domains (**wildpiginfo.msstate.edu**, **feralhogs.tamu.edu**, **tpwd.texas.gov**, etc.) — relevant for **authority** content, different from **Buy Now** SERPs.

---

## HogEye visibility in this research pass

| Check | Result (this bundle) |
| ----- | --------------------- |
| **`hogeyecameras.com` in top ~10 organic** for **55** sampled SERPs | **Yes** for **2** queries: **`hog camera`**, **`remote hog trap trigger`** (`serp_summaries`) |
| **LLM mentions** — niche system query | **Yes** for **`wild hog monitoring camera system`** (`our_domain_in_sources` in `llm_summaries`) |
| **ChatGPT scraper** | **7** tasks in `chatgpt_research` — compare **Vosker / Reolink**, checklists, blog angles, E-E-A-T, AI citation patterns |

**Interpretation:** HogEye can **surface on hog-specific and remote-trigger** SERPs in this snapshot, while **broad trail/solar** rows remain **brand- and marketplace-heavy**. **LLM citation** is **not guaranteed** per query — **one** of **14** mention samples cited the domain.

---

## Backlink scale (DataForSEO `backlinks/live` totals)

| Domain | Reported backlink rows (`total_count`) |
| ------ | -------------------------------------: |
| hogeyecameras.com | 83 |
| vosker.com | 5,005 |
| reolink.com | 103,032 |
| spartancamera.com | 1,489 |
| barnowltech.com | 0 |

**Interpretation:** HogEye is **not** playing the same **link-volume game** as **Reolink**-scale brands — **niche relevance** (trapping, land management, regional) matters more than parity.

---

## Strategic implications

- **Head “cellular trail camera”**–style demand is **editorially and brand-dominated**; this run **prioritizes hog/trap SERPs first** so planning matches **stated positioning**.  
- **Differentiation:** **Hog trapping**, **remote trigger**, **ranch power**, and **field-tested** workflows — in **titles, H1, and comparison** pages.  
- **Competitor conquesting:** **Comparison** and **vs** pages align with how buyers research **before** shortlisting brands.  
- **AI surfaces:** Where **AI Overviews** appeared (**4** / **55** SERPs in this bundle), **clear, quotable** answers on owned pages support both classic and AI-mediated discovery.

---

## Evidence snapshot

| Item | Detail |
| ---- | ------ |
| SERP pulls summarized | **55** (`serp_queries_chosen` / `serp_summaries`) |
| AI Overview present (sample) | **4** / **55** SERPs |
| Labs ranked domains | **hogeyecameras.com**, **vosker.com**, **reolink.com**, **spartancamera.com**, **barnowltech.com** |
| Merged niche keywords | **280** |
| Approx. API bundle cost | **~$2.45** (`approx_total_cost_usd`) |

**Caveat:** **barnowltech.com** was used as the Barn Owl / RangeCam host for Labs; **confirm** the live marketing domain if it differs.
