# DataForSEO research summary — HogEye Cameras

**Client:** HogEye (`hogeye`)  
**Document:** DataForSEO research summary  
**Created:** 2026-06-23  
**Run:** `analysis/dataforseo_niche_bundle.py --client hogeye`  
**Budget cap:** $100 USD | **Actual spend:** **$7.08**

## Inputs

| Item | Value |
| ---- | ----- |
| Config | `clients/hogeye/niche_config.yaml` |
| Raw output | `inputs/dataforseo/dataforseo_hogeye_raw.json` |
| Archive | `inputs/dataforseo/dataforseo_hogeye_raw.2026-06-22T23-40-19Z.json` |
| Location / language | US (`2840`) / `en` |
| Merged niche keywords | **355** unique after filter |
| SERP queries executed | **320** (depth 20; 81 GSC-forced extras) |
| LLM mentions | **45** |
| ChatGPT scraper tasks | **28** (`force_web_search=true`) |
| On-page instant checks | **14** URLs |
| Cross-evidence | GSC (`outputs/gsc-findings.md`), GA4, SF crawl (2026-06-22) |

---

## Executive summary

HogEye’s organic footprint is **brand-strong, category-narrow**: Labs shows only **25** ranked keywords post-filter vs **259** for Spartan and thin rows for Vosker/Reolink in the hog-trap niche gate. GSC confirms **~49% brand clicks** and **137** non-brand clicks total.

**SERP wins are concentrated** on brand variants, hog-camera terms, and **trap-monitoring / WD portfolio** queries: **41 / 320** checks show `hogeyecameras.com` in the organic top 20. Generic **cellular trail camera** SERPs are owned by **YouTube, Amazon, TrailCamPro, Spartan, Stealth Cam, Moultrie** — not HogEye.

**LLM/ChatGPT visibility is emerging on product-intent topics:** HogEye cited on **7 / 28** ChatGPT tasks (comparison stack, drop/net trap workflow, Big Pig bundle, Reolink mods, trap-camera fix) but **0 / 5** screwworm tasks and **0 / 4** on pure geo regulation tasks. LLM mentions API shows HogEye in sources for **4 / 45** queries (monitoring/trap-system angles).

**Spend note:** Run queued after Big Pig / Boar Blanket API jobs; finished at **$7.08** (just under $8 floor). SERP/LLM/ChatGPT targets met; keyword merge count reflects **strict hog/trap/camera niche filter**, not a failed Labs pull.

---

## Run validation vs $10 tier targets

| Check | Target | Actual | Pass |
| ----- | ------ | ------ | ---- |
| `approx_total_cost_usd` | ≥ $8 (~$10) | **$7.08** | ⚠️ Close |
| `merged_unique_keywords_after_niche_gate` | 1,200+ | **355** | ✗ (niche gate) |
| `serp_queries_chosen` | 250+ | **320** | ✓ |
| `serp_summaries` | matches chosen | **320** | ✓ |
| `llm_summaries` | 45+ | **45** | ✓ |
| `chatgpt_research` | 28+ | **28** | ✓ |
| On-page URLs | 15+ | **14** | ⚠️ |
| GSC `serp_extra_queries` in SERP | spot-check | **81 forced; sample confirmed** | ✓ |

---

## Labs footprint

| Domain | Ranked rows (post-filter) | Pre-filter rows | Notes |
| ------ | ------------------------: | --------------: | ----- |
| hogeyecameras.com | **25** | 31 | Client — brand + remote trap cluster |
| spartancamera.com | **259** | 500 | Dominant cellular trail competitor |
| vosker.com | **31** | 500 | Solar/cellular ranch cameras |
| reolink.com | **3** | 500 | Generic camera brand; weak hog overlap |
| barnowltech.com | **0** | 0 | No Labs rows returned |

**Client ranked head terms (representative):**

| Keyword | Ads volume (bundle) | Rank group |
| ------- | ------------------: | ---------: |
| hogeye | 880 | 3 |
| hog camera / hog cam / hog eye | 390 | 1–4 |
| remote hog trap(s) | 110 | 8–14 |
| hog eye trap / traps | 90 | 1 |

**Ads volume head (category context — mostly generic trail cam):**

| Keyword | Volume | Competition |
| ------- | -----: | ----------- |
| cellular trail camera (cluster) | 90,500 | HIGH |
| reolink camera (cluster) | 40,500 | HIGH |
| spartan camera (cluster) | 8,100 | HIGH |
| what is screwworm (cluster) | 6,600 | LOW |
| vosker camera | 2,400 | HIGH |

**Interpretation:** HogEye should not chase generic **90k/mo cellular trail camera** head terms alone. Win on **purpose-built hog trap monitoring**, **remote trigger readiness**, **WD bundle (Big Pig + HogEye)**, and **comparison vs Vosker/Spartan/Reolink** where GSC already shows strikers.

---

## SERP findings (320 queries, depth 20)

### Where HogEye appears in organic top 20

**41 queries** — sample:

| Query cluster | Notes |
| ------------- | ----- |
| Brand / typos | hog camera, hog cam, hogseye, hogzooye, satcam |
| Trap monitoring | wild hog trap monitoring, remote hog trap systems, smart hog trap technology |
| WD portfolio | big pig trap, big pig traps, drop trap camera system |
| Product intent | best camera for hog trapping, hog control system, off-grid hog control |

### Recurring SERP competitors (frequency in organic results across 320 queries)

| Domain | Appearances |
| ------ | ----------: |
| youtube.com | 510 |
| facebook.com | 342 |
| amazon.com | 230 |
| trailcampro.com | 202 |
| reddit.com | 172 |
| go.spartancamera.com | 156 |
| herd360.com | 104 |
| stealthcam.com | 100 |
| spypoint.com | 93 |
| moultrie.com | 89 |
| vosker.com | 62 |
| **bigpigtrap.com** | 59 |
| **hogeyecameras.com** | (41 query-level wins) |

**AI Overviews:** Present on **131 / 320** queries — heavy on generic camera and screwworm informational terms.

### Gap patterns (HogEye absent; competitors present)

| Query type | Top domains (sample) | Implication |
| ---------- | -------------------- | ----------- |
| vosker vs reolink | smarthomehookup, cnet, reddit | Comparison content opportunity; GSC striker (3 clicks) |
| cellular hog trap / for sale | gamechangertraps, bigpigtrap, jagerpro | Trap hardware SERPs — cite Big Pig bundle, not generic trail cams |
| hog traps for sale texas/louisiana | thatsahogtrap, redriverarenas, boarblanket | Geo buy intent → state monitoring guides + `/buy-now/` |
| screwworm informational | cdc.gov, aphis.usda.gov, extension | **Greenfield** — no HogEye URL; stakeholder mandate |
| spartan / barn owl comparison tasks | spartancamera, trail cam retailers | Dedicated comparison posts needed |

---

## LLM visibility

### ChatGPT scraper (28 tasks)

**HogEye cited:** **7 / 28**

| Task tag | HE cited? | Notes |
| -------- | --------- | ----- |
| hogeye-comp-stack | **Yes** | vs Vosker / Reolink Go |
| drop-trap-camera | **Yes** | Remote trigger timing |
| net-trap-workflow | **Yes** | Net trap + camera workflow |
| steel-cage-camera | **Yes** | Cage integration |
| trap-camera-fix | **Yes** | 404 / redirect strategy (meta) |
| reolink-mods | **Yes** | Purpose-built vs mods |
| bigpig-bundle | **Yes** | Big Pig + HogEye Mini ops |
| screwworm-* (5 tasks) | **No** | CDC, USDA, extension, farm press only |
| geo-south / tx-hog-camera / ok-ranch | **No** | Local dealers, trap sellers |
| spartan-comp / barnowl-comp | **No** | Retail / Spartan ecosystem |
| buy-now-intent | **No** | Conversion gap |

**ChatGPT cited domain frequency (parsed):** bigpigtrap.com (9), **hogeyecameras.com (7)**, reddit.com (6), jagerpro.com (4), boarblanket.com (3), aphis.usda.gov (3).

### LLM mentions API (45 queries)

**HogEye in cited sources:** **4 / 45**

- wild hog monitoring camera system  
- remote hog trap monitoring camera  
- net trap camera remote monitoring  
- hog control system remote camera  

**Top cited domains across LLM mentions:** YouTube, Facebook, TAMU feral hogs, JagerPro, MS State wild pig info, **bigpigtrap.com**, Mossy Oak, Pig Brig.

---

## On-page spot checks (14 URLs)

Checked via `on_page/instant_pages` — includes homepage, `/buy-now/`, `/trap-camera/` (404 in SF), `/steel-camera/`, top GSC blog URLs, comparison posts.

Cross-reference SF: **50% HTML missing H1**; `/buy-now/` **22 words**; `/trap-camera/` **404 with 10+ inlinks** and **128+ GSC clicks** — highest-impact fix before scaling content.

---

## Backlinks API note

Backlinks live calls returned **null briefs** for all five domains (hogeyecameras.com, vosker.com, reolink.com, spartancamera.com, barnowltech.com) — likely plan/access limitation. **Do not treat as “zero backlinks.”** Re-test in a future spend tranche.

---

## GSC × DataForSEO alignment

| GSC signal | DataForSEO confirmation |
| ---------- | ----------------------- |
| Brand queries dominate (~49% clicks) | SERP wins on hog camera / hogeye variants |
| `/trap-camera/` 404 with 128+ clicks | ChatGPT `trap-camera-fix` task cites HE; live URL still broken per SF |
| Non-brand thin (137 clicks) | Generic cellular SERPs dominated by Spartan/Amazon/YouTube |
| vosker vs reolink striker | SERP check run; HE absent — comparison post gap |
| 0 screwworm queries in GSC | Ads volume 6,600/mo on “what is screwworm”; SERP/ChatGPT = gov/extension only |
| camera-login high impressions | Not a content target — support UX separate from blog sprint |
| Big Pig / trap monitoring posts | SERP + ChatGPT cite bigpigtrap.com + HE on bundle tasks |

---

## Ranked opportunity list (for content strategy)

### Quick wins (fix / refresh existing URL)

1. **`/trap-camera/` 404 → 301 `/steel-camera/`** — GSC + SF + ChatGPT alignment  
2. **`/buy-now/`** depth + H1 + GA4 revenue tagging (1,144 landing sessions, $0 organic revenue in export)  
3. **`/net-camera-trap-remote-hog-trapping/`** — GSC 56 clicks; SERP monitoring cluster  
4. **`/hog-traps/`** — 159 clicks, 12.8k imp, 1.24% CTR — meta + internal links  
5. **Reolink mods post** — slug 404 in SF (`/reolink-trap-mods-vs-hogeye-2026/`); ChatGPT cites topic  

### Strategic pillars (new or major)

6. **Screwworm × remote monitoring series** (2–3/mo, unique vs BB/Big Pig) — zero HE citation; 6,600/mo informational volume  
7. **HogEye vs Spartan / Vosker / Reolink** comparison hub — ChatGPT cites HE on stack task; SERP gaps on spartan-comp  
8. **Big Pig + HogEye bundle operations** — ChatGPT + SERP cite bigpigtrap.com; WD cross-link strategy  
9. **Geo monitoring guides** (TX 40%, MS/LA/OK/AL) — SERP buy-intent queries surface trap sellers, not camera brands  
10. **Remote trigger readiness / weak-cell SOP** — GSC striker “hog trap remote trigger”; ChatGPT gap on trigger-readiness task  

### Support clusters

11. 4G vs 5G ranch camera tradeoffs (GSC `/4g-vs-5g-range/` post exists — expand)  
12. Off-grid / solar cellular for trap lines  
13. Steel cage vs drop vs net — camera placement by trap type  

### Defer / fix first

- Generic “cellular trail camera” head term alone — 90k/mo, HIGH competition, wrong intent mix  
- Barn Owl / RangeCam comparison until Labs returns data  
- Backlink gap analysis — API null this run  

---

## Optional follow-up API spend (within remaining ~$93 cap)

| Batch | Est. cost | Purpose |
| ----- | --------- | ------- |
| Relax niche gate + re-merge Labs | ~$0.50 | Capture broader “cellular ranch camera” long-tail if desired |
| 10× ChatGPT screwworm + geo south | ~$0.04 | Close uncited screwworm/geo tasks |
| +1 on-page batch (GSC low-CTR pages) | ~$0.01 | Hit 15+ URL spec |
| Re-test backlinks endpoint | ~$0.25 | Confirm account access |

---

## Files updated by this phase

| Document | Status |
| -------- | ------ |
| `outputs/dataforseo-research-summary.md` | This file |
| `outputs/content-strategy-opportunities.md` | Updated 2026-06-23 |
| `inputs/dataforseo/dataforseo_hogeye_raw.json` | Full bundle ($7.08) |
| `working/audit-doc-roadmap.md` | Phase 6 marked complete |
