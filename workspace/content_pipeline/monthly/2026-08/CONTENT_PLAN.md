# August 2026 content plan — HogEye Cameras

**Publication month:** 2026-08  
**Period field:** `2026-08`  
**Research basis:** `workspace/content_pipeline/research/sprint_20260622_audit/`  
**Contract:** **5 posts/mo** Jul–Aug (10/mo from Sep)  
**Approval:** Schell before WordPress draft push / hub publish  
**Roadmap parent:** `workspace/SEO_STRATEGY_JUL_DEC_2026.md` (August table reconciled 2026-07-23)

---

## July inventory (source of truth — do not duplicate)

| ID | Title | Cluster |
| -- | ----- | ------- |
| jul26_01 | What Is New World Screwworm and How Does It Spread? | Screwworm theme 1 |
| jul26_02 | Why Feral Hogs Drive Screwworm Spread Risk | Screwworm theme 2 |
| jul26_03 | How to Spot New World Screwworm (Landowner Guide) | Screwworm theme 3 |
| jul26_04 | Texas Remote Hog Trap Monitoring: Field Guide | Geo TX |
| jul26_05 | HogEye vs Vosker vs Reolink Go for Hog Trapping | Comparison |

**Hard rule:** No August article targeting “how to spot screwworm” or another general screwworm awareness topic.

---

## Strategic frame

| Signal | Implication for August |
| ------ | ---------------------- |
| July used 3 screwworm pillars | Replace planned duplicate awareness slot with **HogEye Mini Starlink** product article |
| Original `aug26_01` fly/unmonitored concept cannibalized jul26_02 | Re-scope to **trap-site check-in SOP** (ops only) |
| ChatGPT spartan-comp uncited; Spartan Labs dense | Ship **HogEye vs Spartan** |
| GSC LA hog-trap buy intent; Jul covered TX | Ship **LA/MS humid** geo monitoring |
| GSC `drop trap camera system` striker | Ship **drop trap camera placement + timing** |

Every piece must pass `workspace/NORTH_STAR_POSITIONING.md` and `workspace/brand_truth/BRAND_BASELINE.md`.

**Cross-brand uniqueness:** HogEye = monitoring / alerts / remote trigger. Boar Blanket = trapping / landscape. Big Pig = trap operations / removal at scale. Do not write BB trap-type or BPT ops deep-dives.

---

## August allocation (5 new posts)

| ID | Working title | Primary keyword | Cluster | Rationale |
| -- | ------------- | --------------- | ------- | --------- |
| **aug26_01** | Remote Trap-Site Check-In SOP: Alerts, Status, and When to Drive | hog trap remote check-in | Workflow / ops | Practical check-in cadence using camera alerts + trap status; on-site verification rules. Not geo (vs jul26_04). Not screwworm awareness. |
| **aug26_02** | HogEye Mini Starlink: Remote Hog Trap Monitoring Without Cellular Service | remote hog trap monitoring | Product / connectivity | Official Mini + Starlink bundle for sites with no/unreliable cellular. Confirmed product facts only. Replaces duplicate screwworm `aug26_02`. |
| **aug26_03** | HogEye vs Spartan for Hog Trap Lines | spartan camera hog trap | Comparison | Purpose-built trap monitoring vs general Spartan cellular trail cameras. Distinct from jul26_05. |
| **aug26_04** | Cellular Hog Trap Camera Setup for Humid Louisiana and Mississippi Lines | hog trap camera louisiana | Geo LA/MS | Humidity, canopy, bottoms; placement for Gulf trap lines. Distinct from TX field guide. |
| **aug26_05** | Drop Trap Camera Placement and Trigger Timing | drop trap camera system | Workflow | Placement + when to close on a drop/panel drop system. |

### Parallel (not a sixth post)

| Item | Action | Note |
| ---- | ------ | ---- |
| `/net-camera-trap-remote-hog-trapping/` | Refresh meta, H1/copy depth, internal links as needed | Page update only; track in `PAGE_UPDATES_AUGUST.md` when work starts |

---

## Screwworm / WD coordination

- August: **0** new screwworm posts (July covered themes 1–3).
- Resume Sep+ on geo / seasonal / ops axes per Jul–Dec §5 and `screwworm-topic-matrix.md`.
- If any ops piece mentions flies or carcass pressure, keep it trap-ops only and do not re-teach NWS basics.

---

## Pipeline checklist

- [x] Queue seeded (`queue/monthly_queue.csv`)
- [x] 5 briefs (`briefs/aug26_*_brief.md`)
- [ ] Research packs (optional if drafts cite sprint audit directly)
- [x] 5 WP JSON drafts (`content/posts/aug26_*_wp_draft.json`)
- [x] Humanizer + QA for **aug26_01, 03, 04, 05** → READY for human review
- [ ] **aug26_02 HOLD** until Schell/Robbie confirm Starlink hardware price ($1,299 page vs $2,999 email) and buy path
- [x] Hub push for **aug26_01, 03, 04, 05** → hub **approved** then WP **drafts** (2026-08-21; ids 500485–500488)
- [ ] Hub push for **aug26_02** after pricing confirm
- [x] `pull-approved --apply` for the four approved posts
- [x] WordPress **drafts** after apply (not live)
- Review index: [`READY_FOR_REVIEW.md`](READY_FOR_REVIEW.md)

---

## Evidence pointers

| ID | Evidence |
| -- | -------- |
| aug26_01 | Ops longevity axis (Jul–Dec §5); North Star wasted-trips / closure timing |
| aug26_02 | Remote hog trap / remote hog trap monitoring cluster (DataForSEO summary); confirmed Starlink product facts from operator brief |
| aug26_03 | Spartan Labs 259 rows; ChatGPT spartan-comp uncited |
| aug26_04 | GSC `hog traps for sale in louisiana`; geo-south ChatGPT gap |
| aug26_05 | GSC `drop trap camera system` 213 imp pos 9.3; ChatGPT drop-trap-camera cited |

Raw bundle: `research/sprint_20260622_audit/inputs/dataforseo/dataforseo_hogeye_raw.json`

---

## Source documents

- `workspace/SEO_STRATEGY_JUL_DEC_2026.md`
- `SEO_STRATEGY.md`
- `workspace/brand_truth/BRAND_BASELINE.md`
- `../research/sprint_20260622_audit/stakeholder/wildlife-dominion/screwworm-topic-matrix.md`
- `../research/sprint_20260622_audit/working/screwworm-content-guidelines.md`
- `../2026-07/CONTENT_PLAN.md` + `content/posts/jul26_*_wp_draft.json`
