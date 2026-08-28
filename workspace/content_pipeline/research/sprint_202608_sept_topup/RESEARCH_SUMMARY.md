# RESEARCH_SUMMARY — HogEye Sept 2026 top-up (Mini AI + deer-season monitoring)

**Date:** 2026-08-14  
**Repo path:** `workspace/content_pipeline/research/sprint_202608_sept_topup/`  
**Run:** Advanced SEO Analysis `analysis/dataforseo_niche_bundle.py --client hogeye-sept-topup` + volume/Labs expansion top-up  
**Location / language:** US `2840` / `en`  
**Spend actual:** **$7.97** (bundle $7.11 + expansion $0.76 + seed volume $0.09)  
**Soft ceiling:** $100 — not hit. Remaining budget was not spent because **Labs/Ads volume on these clusters is structurally empty**, not because the pass was cheap-capped.

This pass does **not** write briefs, drafts, or packs. It does **not** replace `CONTENT_PLAN.md`.

---

## Coverage vs quality bar

| Bar | Target | Actual | Verdict |
| --- | ------ | ------ | ------- |
| SERP | depth 20; every seed group + GSC adjacent | **130** in-cluster (depth 20) + **77** expansion SERPs | Pass on seeds/GSC. Expansion then leaked generic deer-corn retail / wild-boar trivia — stopped adding *cluster* signal |
| LLM mentions | 45+ in-cluster | **52** | Pass |
| ChatGPT scraper | 28+ in-cluster, `force_web_search` | **32** / 32 (`force_web_search=true`) | Pass |
| Suggest + related + volume | until Mini-AI-adjacent and deer-monitoring variants stop adding signal | Exact cluster seeds: **0 Labs suggestions** on 43/44 suggest seeds and 24/26 related seeds. Broader adjacent seeds added feeder/corn/AI-trail terms, then degenerated | Pass — variants stopped. Empty Labs is a demand finding, not a skipped step |
| On-page | money URLs that new pieces will interlink | **16** URLs | Pass |
| Spend | not a $2–3 snapshot | **$7.97** (LLM mentions were **$5.35** of the bundle) | Pass vs cheap-cap; further ChatGPT would not create Ads volume that does not exist |

June $10-tier comparison: June spent **$7.08** on a **355-keyword** hog/trap/screwworm universe. This pass spent the same order of money on **two new clusters**. The keyword graph for Mini-AI and deer-plot *camera* queries is not there in Google Ads/Labs.

---

## Existing evidence mined (not the whole study)

June sprint (`sprint_20260622_audit/`) never scored deer-prep or Mini AI.

| Source | Deer / plot / feeder / acorn | AI / detection / hog-alert | Remote check-in / drop-trap / Mini |
| ------ | ---------------------------- | -------------------------- | ---------------------------------- |
| GSC Queries.csv (to 2026-06-20) | **0 rows** | `feral animal detection technology` (1 imp); `object detection reolink cameras` (1 imp) | Remote-trigger cluster is real: `remote hog trap` 236 imp; `remote hog trap trigger` 172; `drop trap camera system` 213 imp pos 9.3; `wild hog trap monitoring` 239; `smart hog trap technology` 206; `hogeye mini camera` 6 clicks / 32 imp |
| June DataForSEO | not scored | not scored | ChatGPT cited HE on trap monitoring / comparison / Big Pig Mini *bundle* — not species AI |
| Brand baseline | Mini is the **$1,299** flagship camera (no AI feature sheet) | Do not invent Mini AI | `/buy-now/`, `/camera-resources/`, `/hog-traps/`, `/steel-camera/` |

---

## Demand table (Ads volume is not the whole story)

Google Ads search_volume on **189** cluster seeds (queries >10 words skipped): **7 nonzero**.

| Keyword | Ads vol | Competition | Role |
| ------- | ------: | ----------- | ---- |
| remote hog trap / remote control hog trap | 110 | HIGH | June cluster; still the commercial backbone for “don’t drive unless it matters” |
| hog trap remote trigger / remote hog trap trigger | 70 | HIGH | GSC + aug26_01 SOP adjacency |
| electronic hog trap | 40 | MEDIUM | Hardware, not AI |
| feral animal detection technology | 10 | LOW | Only GSC detection striker with volume |
| reolink animal detection | 10 | HIGH | Competitor AI term |
| **All Cluster A Mini-AI seeds** (AI hog camera, hog count camera, false alerts hog camera, HogEye Mini AI, …) | **0** | — | No Ads graph. **SERP still exists** (see below) |
| **All Cluster B camera seeds** (hogs at deer feeder camera, food plot hog damage camera, check hog trap without driving, screwworm deer camera, …) | **0** | — | No Ads graph. Adjacent *problem* queries do have volume |

**Broader Labs (expansion) — adjacent terms that *do* have volume:**

| Keyword | Ads vol | Notes |
| ------- | ------: | ----- |
| yellowstone ai trail camera | 170 | Owns generic “AI trail camera” SERP with Browning |
| wild hog damage | 110 | Informational; not camera-specific |
| ai trail camera | 50 | Generic AI trail-cam head — **not** the HE fight |
| how to keep hogs away from deer feeder | 40 | Best Cluster B *problem* term |
| jager pro camera | 40 | Hog-specific camera competitor |
| animal detection camera | 20 | Security/Lorex/Reolink mix |
| how to get rid of hogs at deer feeder / keep hogs out of deer corn | 10 | Forum SERPs (Realtree, Reddit, AccurateShooter) |
| how to keep hogs from eating deer corn | 10 | Same as GSC-era adjacent |

**Interpretation:** Do not kill these clusters because Ads volume is 0. People (and ChatGPT) ask the long-tails; Google just does not bill them as keywords. HE already appears in organic top 20 on **29/53 Cluster A** queries and **6/48 Cluster B** queries. LLM mentions: **0/52**. That is the gap.

Skip generic `cellular trail camera` (90k, June). Skip Starlink pricing (August hold).

---

## Citation landscape (who gets named for “detects animals / fewer false alerts”)

ChatGPT (`force_web_search`) ranking for **hog-specific alerts**, not generic trail-cam roundups:

| Who ChatGPT cites | What it claims | Hog-specific? |
| ----------------- | -------------- | ------------- |
| **Moultrie EDGE / Smart Tags** | Hog vs deer vs raccoon alerts | **Yes** — current default recommendation |
| **JAGER PRO M.I.N.E.** | Purpose-built feral hog cellular camera | **Yes** — trap-system, not trail cam |
| **Yellowstone AI / Browning AI** | Generic AI trail camera | Species AI marketing; not trap-ops |
| **Vosker Sense** | Filter people/vehicles | **No** — not hog-class |
| **Spartan** | Support docs on wind/vegetation false triggers | **No** hog-class in these tasks |
| **Reolink** (Go Ranger PT + animal detection) | Animal/person/vehicle | Weak hog-trap fit; DIY-mod category |
| **Barn Owl RangeCam** | Animals / people / vehicles | **Not hog-specific** (ChatGPT said this explicitly) |
| **BoarBuster / TrapSmart** | Smart *trap* systems | Trap hardware, not HE’s camera lane |
| **HogEye** | Cited on **4/32** tasks: trap-cam vs trail cam; live push; branded Mini; vs-stack | Cited as **trap monitoring**, not as species-AI |

LLM mentions API (Google, 52 queries): top domains YouTube, Facebook, Reddit, Amazon, Mossy Oak Gamekeeper, APHIS, TAMU feral hogs, JagerPro, TrailCamPro. **hogeyecameras.com = 0**. Highest mention counts: “hog camera that detects hogs” (61), “vosker AI camera false alerts” (53), “hogs at deer feeder camera” (16).

SERP organic frequency (130 in-cluster queries): facebook 257, youtube 187, **hogeyecameras.com 79**, jagerpro 54, reddit 51, pigbrig 46, gamechangertraps 42, bigpigtrap 38, spypoint 35, deerhunterforum / deeranddeerhunting on plot queries.

**Cluster B extra SERP** (`how to keep hogs away from deer feeder`, etc.): HE **absent**. Forums and Realtree own it. That is the deer-prep opening — if HE writes “see the feeder remotely / only drive when the sounder is on it,” uniqueness vs BB (whole-sounder on the plot) and BPT (remove the sounder) is clean.

---

## On-page (interlink targets)

| URL | Status | Use from new Sept pieces |
| --- | ------ | ------------------------ |
| `/hog-traps/` | 200 | Money URL — refresh still valid |
| `/buy-now/` | 200 | Mini/buy path (thin page still) |
| `/shop/` | 200 | Same buy template |
| `/steel-camera/` | 200 | Cage/corral monitoring |
| `/camera-resources/` | 200 | Mini vs Legacy setup — **do not scrape this as Mini AI proof** |
| `/net-camera-trap-remote-hog-trapping/` | 200 | Net workflow |
| `/hog-trapping-cameras-compared-2026-hogeye-vs-trail/` | 200 | Comparison hub |
| `/what-is-new-world-screwworm/` | **200** | July pillar **already live** |
| `/hog-trap-remote-check-in-sop/` (aug26_01) | **404** | Mini-AI follow-up should wait until this SOP is live, or ship SOP first |
| `/hogeye-mini-starlink-remote-hog-trap-monitoring/` (aug26_02) | **404** | Starlink product not live; do not research Starlink pricing |
| `/hogeye-vs-spartan-hog-trap-camera/` (aug26_03) | **404** | Comparison not live |
| `/blog-hogeye-vs-vosker-cellular-cameras-comparison/` | **404** | Old Sept “refresh Vosker post” target is currently 404 |
| `/reolink-vs-vosker-vs-hogeye-off-grid-camera-comparison/` | **404** | Same |
| `/trap-camera/` | **404** | Still broken (June P0) |

---

## Season calendar (Cluster B timing)

Full table with source URLs: [`deer_season_calendar.md`](deer_season_calendar.md).

| State | Archery (earliest) | Gun / firearms (earliest general) |
| ----- | ------------------ | --------------------------------- |
| TX | **Oct. 3, 2026** | **Nov. 7, 2026** |
| MS | Velvet **Sept. 11–13**; regular **Oct. 1 / Oct. 15** by unit | Gun with dogs **Nov. 21** |
| LA | **Sept. 19** (Areas 3, 7, 8, 10); **Oct. 1** (Areas 1, 2, 4) | Still-hunt **Oct. 17** earliest |
| OK | **Oct. 1, 2026** | Deer gun **Nov. 21–Dec. 6** |
| AL | **Oct. 1** (Zones D/E) / **Oct. 15** (A/B/C) | Private gun **Nov. 21** (D/E gun windows from **Nov. 7**) |

September copy is **in-season** for MS velvet and LA early archery; still **prep** for TX/OK/most of AL.

---

## Flag: old Sept skeleton vs July inventory

`workspace/SEO_STRATEGY_JUL_DEC_2026.md` September still lists:

> Screwworm (3): **“What is screwworm” landowner pillar**; wildlife vs cattle monitoring blind-spot; TX ranch biosecurity checklist.

July already shipped matrix themes 1–3. Live URL:

- `https://hogeyecameras.com/what-is-new-world-screwworm/` — title **“What Is New World Screwworm and How Does It Spread?”** (`jul26_01`, primary **what is screwworm**)

**Cut that Sept pillar.** Do not write another definition piece. The contract still wants 2–3 screwworm posts/mo — fill with **NWS → deer / wildlife camera observation** (ChatGPT + APHIS: USDA has used **130+ trail cameras in Texas** watching wildlife), not “what is screwworm” again.

---

## Recommended HE Sept slot changes (10-post mix — recommendation only)

Uniqueness lock for every new piece:

- **HE** = see it remotely; only drive when it matters  
- **BB** = whole-sounder *on the plot*  
- **BPT** = remove the sounder  
- **Never** use “hog trap lines” in a recommended title  
- **Never** lock a primary keyword to “HogEye Mini AI” / “HogEye AI camera” until Schell names the product  
- **Never** invent Mini AI features, price, SKU, or how thresholds work

| # | Action | Slot | Primary language (generic) | Why |
| - | ------ | ---- | -------------------------- | --- |
| 1 | **CUT** | Old Sept “what is screwworm” pillar | — | Duplicate of live `jul26_01` |
| 2 | **ADD** | Mini AI / hog-specific alerts — **follow-up to aug26_01 SOP** | hog camera alerts / camera that notifies when hogs / reduce false alerts hog camera (0 Ads; HE already in SERP top 20) | Demand is LLM/ChatGPT + SERP, not Ads. Cite Moultrie/Jager as the current AI-alert incumbents; HE angle = trap-site check-in, not a fake spec sheet. **Hold product claims for Schell.** Secondary only: HogEye Mini AI |
| 3 | **ADD** | Deer-prep monitoring (all-brand theme, HE lens) | how to keep hogs away from deer feeder (40) + remote check without driving | Forum-owned SERP; HE absent. Plots/corn/feeders/acorns/bucks-leave as support, not bait how-tos |
| 4 | **RE-ANGLE** | NWS slot #1 | NWS wildlife / deer camera monitoring Texas (observation) | Replaces duplicate pillar. APHIS camera-surveillance fact is the hook. Educational, `trust_sensitive` |
| 5 | **RE-ANGLE** | NWS slot #2 | Wildlife vs cattle visibility gap → **deer/wildlife cameras vs cattle checks** | Keep the blind-spot idea; point it at deer season + feeders, not another awareness explainer |
| 6 | **KEEP** | `/hog-traps/` refresh | hog traps / remote hog trap | 159 clicks, 12.8k imp, 1.24% CTR — still the money URL new posts should hit |
| 7 | **KEEP / fix URL** | Barn Owl vs HogEye | barn owl rangecam vs hogeye (comparison) | ChatGPT: Barn Owl is not hog-specific. Strong Sept comparison once aug26_03 Spartan is not duplicating the same frame |
| 8 | **RE-ANGLE** | OK geo | oklahoma deer season hog camera remote check | Old “OK off-grid ranch camera” is weaker than deer-opener **Oct. 1** + remote check-in |
| 9 | **RE-ANGLE** | AL **or** TX geo | alabama/texas hog food plot camera before archery | TX archery **Oct. 3** is the bigger ad-weight play; AL Oct. 1/15 if TX is already covered in July/Aug |
| 10 | **DEFER or restore** | Vosker refresh / net-trap / steel-cage | — | Vosker “refresh” URL is **404**. Net-trap and steel-cage were June ChatGPT hits already cited — lower priority than Mini AI + deer-prep |

If only three new-theme slots fit besides NWS/geo/refresh: **(2) Mini-AI follow-up, (3) deer-feeder remote monitoring, (4) NWS-to-deer observation.**

Do not ship the Mini-AI article as a product announcement until Schell facts land. It can still be a **demand/problem** piece (false alerts, count thresholds as *questions*, wasted drives) that interlinks the SOP + `/buy-now/` + `/hog-traps/`.

---

## Open questions blocked on Schell (Mini AI facts)

Do **not** invent answers in briefs later:

1. Public product name (Mini AI vs unnamed detection/alerts on Mini vs HE+BPT SKU split)  
2. Whether hog-count thresholds **1 / 3 / 5+** are shipping, beta, or concept  
3. What is detected (hog vs deer vs motion zone vs count) — ChatGPT already hallucinated “motion-detection area” from `/camera-resources/`; that is **not** confirmation  
4. Price, data plan, SKU, HE vs BPT vs Mini feature matrix  
5. Whether “notify at hog-count” is app-side, camera-side, or operator SOP  
6. Any claim of fewer false alerts vs Moultrie/Jager/Yellowstone — needs a fact, not a ranking wish  

Starlink: August hold is a fact-confirm, not a demand gap. Out of scope here.

---

## Files in this folder

| Path | What |
| ---- | ---- |
| `RESEARCH_SUMMARY.md` | This file |
| `deer_season_calendar.md` | Official 2026–27 openers + source URLs |
| `config/niche_config.yaml` | Scoped bundle config |
| `seeds/seed_list.md` | Planned seeds + GSC extras |
| `seeds/executed_queries.md` | SERP 130 + LLM 52 + ChatGPT 32 + top-up 77 |
| `inputs/dataforseo/dataforseo_hogeye-sept-topup_raw.json` | Full bundle ($7.11) |
| `inputs/dataforseo/dataforseo_hogeye-sept-topup_topup.json` | Broader Labs + extra SERP ($0.76) |
| `inputs/dataforseo/dataforseo_hogeye-sept-topup_seed_volume.json` | Ads volume on 189 seeds ($0.09) |

Raw copies also live under Advanced SEO Analysis `clients/hogeye-sept-topup/inputs/dataforseo/` (this repo owns the calendar).
