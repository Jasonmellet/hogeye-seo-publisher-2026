# Content strategy opportunities — HogEye Cameras

**Client:** HogEye (`hogeye`)  
**Document:** Content strategy opportunities  
**Created:** 2026-06-23  
**Evidence:** Screaming Frog (2026-06-22) + GSC (Feb 2025–Jun 2026) + GA4 (property 245859533) + DataForSEO bundle ($7.08)

**Sprint contract:** 5 posts/mo Jul–Aug → 10/mo Sep; 2–3 screwworm posts/mo unique vs Boar Blanket/Big Pig; Schell approval before publish.

This document is the **prioritized opportunity stack** for calendar planning — not the calendar itself.

---

## Strategic frame

| Layer | Finding | Implication |
| ----- | ------- | ----------- |
| **Demand** | Brand GSC clicks ~49%; non-brand **137** total | Grow trap-monitoring + comparison + geo monitoring, not generic trail-cam head |
| **SERP reality** | 41/320 HE wins; YouTube/Amazon/Spartan dominate generics | Own **hog-specific monitoring** and **WD bundle** narratives |
| **LLM reality** | HE cited 7/28 ChatGPT; 0/5 screwworm | Screwworm + geo = citation gaps; comparison stack already wins |
| **Site health** | `/trap-camera/` 404; 50% missing H1; `/buy-now/` thin | Fix URLs + template **before** scaling posts |
| **Commerce** | GA4: organic ~25% sessions but ~$753 revenue vs direct ~$90k | `/buy-now/` tagging + content CTAs need audit |
| **Portfolio** | bigpigtrap.com in SERP + ChatGPT | Cross-brand bundle content with Big Pig agent |

**Geo weighting (ads):** Texas ~40%; MS, LA, OK, AL ~60% combined.

---

## Priority tier 1 — Do first (Jul 2026)

### 1. Technical + conversion fixes (parallel, not optional)

| Action | Evidence | Owner |
| ------ | -------- | ----- |
| **301 `/trap-camera/` → `/steel-camera/`** + fix 10+ inlinks | GSC 128+ clicks; SF 404; ChatGPT trap-camera-fix cites HE | Dev/content |
| Restore or redirect **404 slugs** (reolink mods, baiting guide, common mistakes) | SF crawl; ChatGPT reolink-mods task | Dev/content |
| **H1 + meta template** on HTML 2xx | SF 50% missing H1 | Theme |
| **`/buy-now/`** expand copy, H1, schema; GA4 purchase events | SF 22 words; GA4 $0 revenue on 1,144 sessions | Dev + analytics |

---

### 2. Screwworm content queue (2–3 posts/mo, unique vs BB/Big Pig)

**Why:** Stakeholder mandate; GSC **0** screwworm queries; Ads **6,600/mo** on “what is screwworm”; ChatGPT cites **CDC/USDA/extension only** — no HogEye URL.

**HogEye angle:** Remote monitoring gap — unattended trap lines, fly pressure near carcasses/bait, early detection of sick livestock/wildlife movement, **camera + trigger readiness** as biosecurity ops. Line: *“If it’s on shit, that isn’t it.”* (NWS breeds on live animals.)

| # | Topic | Primary keyword target | Differentiation vs BB/Big Pig |
| - | ----- | ---------------------- | ------------------------------ |
| 1 | Ranch monitoring during screwworm alerts | screwworm ranch monitoring camera | Camera/trigger ops, not trap type |
| 2 | Why unmonitored hog traps increase fly exposure | screwworm feral hogs fly attraction | Remote check-in SOP |
| 3 | What landowners should watch (not clinical vet) | screwworm symptoms landowner | Link to USDA; HE = observation tech |
| 4 | Texas ranch biosecurity checklist | feral hogs screwworm risk texas | TX geo weight |

**Guidelines:** `working/screwworm-content-guidelines.md`

---

### 3. Comparison portfolio (category defense)

**ChatGPT already cites HogEye on comp-stack, reolink-mods, drop/net workflow.**

| Piece | Target queries | Type | Evidence |
| ----- | -------------- | ---- | -------- |
| HogEye vs Vosker vs Reolink Go (2026 refresh) | vosker vs reolink, vosker camera | Update/new | GSC 3 clicks; ChatGPT **Yes** |
| HogEye vs Spartan cellular (trap use case) | spartan camera, spartan trail camera | New | SERP gap; ChatGPT spartan-comp **No** |
| Reolink trap mods vs purpose-built HE | reolink trap mods | Fix 404 + publish | SF 404; ChatGPT **Yes** |
| Barn Owl / RangeCam vs HogEye (ranch line) | barn owl camera ranch | New | SERP/LLM gap |
| Big Pig drop trap + HogEye Mini bundle guide | big pig trap hogeye | New | ChatGPT **Yes**; WD coordination |

---

## Priority tier 2 — Geo monitoring + buy intent

**SERP pattern:** “hog traps for sale {state}” surfaces **trap dealers** (GameChanger, Red River, Boar Blanket) — HE content should target **monitoring + remote trigger** in those states, not compete on “trap for sale” alone.

| State | Opportunity | Type |
| ----- | ----------- | ---- |
| **Texas** | Remote hog trap monitoring guide + weak-cell checklist | New — TX 40% ad weight |
| **Louisiana / Mississippi / Alabama** | Cellular camera setup for humid Gulf climate trap lines | New — geo-south ChatGPT gap |
| **Oklahoma** | Off-grid ranch camera + hog monitoring | New — ok-ranch-camera task uncited |
| **All** | Expand `/4g-vs-5g-range/` and link from state posts | Update |

Internal link pattern: state monitoring post → `/steel-camera/` or `/buy-now/` → Big Pig bundle where relevant.

---

## Priority tier 3 — Trap-type workflows (support cluster)

| Topic | Evidence | Type |
| ----- | -------- | ---- |
| Drop trap camera placement + trigger timing | ChatGPT drop-trap-camera **Yes** | New/update |
| Net trap remote workflow (Boar Blanket coordination) | ChatGPT net-trap-workflow **Yes**; BB in LLM cites | New |
| Steel cage camera integration | ChatGPT steel-cage-camera **Yes** | New |
| Remote trigger readiness SOP (weak LTE) | GSC “hog trap remote trigger”; ChatGPT trigger-readiness **No** | New |
| Year-end gear audit (camera, battery, trigger) | ChatGPT gear-audit task | Seasonal |
| Wild hog damage ROI + monitoring | ChatGPT damage-roi; GSC damage posts | Update |

---

## Priority tier 4 — Brand support & education

| Topic | Evidence | Type |
| ----- | -------- | ---- |
| camera-login UX content (FAQ only — not SEO target) | 653+ GSC clicks | Support, not blog |
| Hog trapping cameras compared 2026 roundup | ChatGPT cameras-compared-2026 **No** | Pillar |
| Smart trap technology standards | SERP win on query; ChatGPT smart-trap-tech **No** | Explainer |
| Cattle vs wild hog monitoring (same ranch) | ChatGPT wildlife-vs-cattle **No** | Differentiation |

---

## Technical prerequisites (parallel track)

Ship from SF **before or alongside** first July posts:

1. **`/trap-camera/`** redirect + inlink cleanup  
2. **H1/meta template** — 50% missing on HTML 2xx  
3. **404 slug restoration** (6 HTML 404s in crawl)  
4. **Mixed content** — HTTP PDFs/images  
5. **www vs apex** canonical preference (`client_config.yaml`)  
6. **GA4** revenue events on `/buy-now/` and shop paths  

---

## Monthly mix suggestion (starting Jul 2026)

| Category | Posts/mo (Jul–Aug) | Posts/mo (Sep+) | Notes |
| -------- | -----------------: | --------------: | ----- |
| Screwworm / biosecurity | 2–3 | 2–3 | Unique vs BB/Big Pig |
| Comparison (Vosker/Spartan/Reolink/Barn Owl) | 1–2 | 2 | ChatGPT-proven angles first |
| Geo monitoring (TX, MS, LA, OK, AL) | 1 | 2–3 | Weight TX |
| Trap workflow / trigger / bundle | 1 | 2 | Big Pig + BB cross-links |
| Refresh / fix (404 recovery, buy-now adjacent) | 0–1 | 1 | Count substantial updates |

**Jul–Aug total:** ~5/mo | **Sep+ total:** ~10/mo — adjust with Schell approval queue.

---

## KPIs by dataset

| KPI | Source | Baseline |
| --- | ------ | -------- |
| Non-brand GSC clicks | GSC | **137** (queries with clicks, no brand token) |
| Brand click share | GSC | ~**49%** |
| `/trap-camera/` clicks | GSC | **128+** (404 in SF) |
| `/buy-now/` landing sessions | GA4 | **1,144** ($0 revenue in export) |
| Organic revenue | GA4 | **~$753** (all organic; tagging audit needed) |
| SERP top-20 presence | DataForSEO | **41 / 320** queries |
| ChatGPT citations | DataForSEO | **7 / 28** tasks |
| LLM mentions (HE in sources) | DataForSEO | **4 / 45** queries |

---

## WD portfolio coordination

| Sister brand | HogEye content handoff |
| ------------ | ---------------------- |
| **Big Pig Traps** | Bundle ops posts; shared SERP on drop trap + camera system |
| **Boar Blanket** | Net trap workflow; link to BB comparison from HE net-camera posts |
| **Wildlife Dominion** | Brand hub queries (“wildlife dominion” 9 GSC clicks) — consistent NAP/links |

Topic deduplication matrix: `clients/wildlife-dominion/working/screwworm-topic-matrix.md`

---

## Deferred until follow-up data spend

- Generic “cellular trail camera” 90k/mo head term  
- Backlink competitive gap (API null)  
- Full 3–6 mo calendar grid (next step after Schell review of this doc)  
- Optional ~$1–3 API top-up for screwworm ChatGPT + niche merge expansion  

---

## Source documents

- `outputs/gsc-findings.md`  
- `outputs/ga4-findings.md`  
- `outputs/technical-findings.md`  
- `outputs/dataforseo-research-summary.md`  
- `outputs/dataforseo-research-plan.md`  
- `working/screwworm-content-guidelines.md`  
- `clients/wildlife-dominion/working/content-sprint-stakeholder-brief-2026-06.md`
