# June 2026 Content Package — HogEye

**Theme:** Operational Excellence + Texas/Regional Authority  
**Created in repo:** May 2026 (for **June publication**)  
**Status:** **Sent to Schell for approval (2026-05-19)** — Google Doc complete; WordPress draft **not** started  
**Live status doc:** [`STATUS.md`](STATUS.md)  
**Strategy doc:** `workspace/SEO_STRATEGY_MAY_JUL_2026.md`  
**Client review (Google Doc):** [Hog Eye | 2026 SEO Strategy & Blueprint](https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit) — **May 2026** tab (executive summary) + sub-tabs **Article 1–5**

---

## Milestone checklist (2026-05-19)

| Step | Status |
| --- | --- |
| Briefs + research packs | ✅ |
| Client-review copy (`google_doc/`) | ✅ Expanded + voice pass |
| Executive summary → **May 2026** tab | ✅ [`COVER_PAGE_EXECUTIVE_SUMMARY.md`](google_doc/COVER_PAGE_EXECUTIVE_SUMMARY.md) |
| Agent batch review (gpt-5.5) | ✅ [`review/BATCH_AGENT_SUMMARY.md`](review/BATCH_AGENT_SUMMARY.md) |
| All articles pushed to Google Doc | ✅ |
| **Schell approval** | ⏳ Pending |
| WP JSON + draft publish | ⏳ After approval |

---

## Google Doc tab ↔ repo mapping

Push with `npm run google:push-tabs -- --month 2026-06` (see [`google_doc/README.md`](google_doc/README.md)).

| Google Doc tab | `article_id` | Client-review file |
| --- | --- | --- |
| **May 2026** (cover) | — | `google_doc/COVER_PAGE_EXECUTIVE_SUMMARY.md` |
| **Article 1** | `jun26_02` | `google_doc/Article_01_trapping_wild_hogs_texas.md` |
| **Article 2** | `jun26_01` | `google_doc/Article_02_hog_trap_placement.md` |
| **Article 3** | `jun26_05` | `google_doc/Article_03_electronic_hog_traps.md` |
| **Article 4** | `jun26_03` | `google_doc/Article_04_multi_trap_operation.md` |
| **Article 5** | `jun26_04` | `google_doc/Article_05_wild_hog_damage_field_guide.md` |

**Recommended draft order after approval:** Article 1 → 2 → 3 → 4 → 5 (Texas anchor first, then ops depth, then visual field guide).

---

## New content (5 pieces)

| # | `article_id` | Title | Primary KW | Vol (DataForSEO Apr) | Cluster |
| --- | --- | --- | --- | --- | --- |
| 1 | `jun26_02` | Trapping Wild Hogs in Texas: Regulations, Permits, and What Landowners Need to Know | feral hogs texas | 1,900/mo | regulatory |
| 2 | `jun26_01` | Hog Trap Placement: Where to Set Traps, How to Read Hog Signs, and What to Do Before You Bait | hog trap placement tips | — | trap-operations |
| 3 | `jun26_05` | Electronic Hog Traps Explained: How Remote Trigger Systems Work | electronic hog trap | 40/mo | remote-closure |
| 4 | `jun26_03` | How to Run a Multi-Trap Hog Operation Across a Large Property | multi trap hog operation | — | trap-operations |
| 5 | `jun26_04` | What Does Wild Hog Damage Look Like? A Field Guide for Landowners | wild hog destruction | 20/mo | damage-driven |

---

## May 2026 posts to link from (live 2026-05-04)

| Piece | Use for internal links |
| --- | --- |
| Feral hog damage costs | ROI + why trapping matters |
| Wild hog behavior & trap timing | movement, scouting, closure timing |
| Hog trap baiting guide | pre-bait and conditioning |
| Common hog trap mistakes | placement and closure errors |
| Corral vs box vs drop net | trap type context |

Confirm live URLs in WP before publish; slugs may differ slightly from registry.

---

## Page updates (5 targets)

See `PAGE_UPDATES_JUNE.md`. Summary:

1. `/smart-ranch-network-how-to-build-a-multi-trap-system/` — link to Article 4 + refresh multi-trap CTA  
2. `/hog-traps/` — add FAQ: Texas regulations + electronic trap basics  
3. `/net-camera-trap-remote-hog-trapping/` — link Articles 2 + 3 (placement + remote trigger)  
4. High-impression blog posts from GSC (pos 8–15) — refresh meta + FAQ once GSC export runs  
5. `/camera-resources/` — hub links to all five June posts after publish  

---

## Internal linking map (once all 5 live)

```
Article 1 (Texas)
  └── links to: May damage, May mistakes, May trap comparison, /hog-traps/

Article 2 (placement)
  └── links to: May behavior, May baiting, May mistakes, Article 1 (TX context)

Article 3 (electronic traps)
  └── links to: May mistakes, May comparison, /net-camera-trap-remote-hog-trapping/

Article 4 (multi-trap)
  └── links to: /smart-ranch-network-how-to-build-a-multi-trap-system/, Articles 2+3, May behavior

Article 5 (field guide)
  └── links to: May damage cost post, Article 1, May mistakes
```

---

## Data inputs (May 2026 planning pass)

| Source | Status | Notes |
| --- | --- | --- |
| DataForSEO gap + PAA | ✅ Reused | `seo/plan/hogeye_keyword_gap_combined.csv`, `hogeye_paa_questions.csv` (2026-04-17) |
| GSC deep export | ⚠️ Blocked | Search Console API disabled on service account project — enable API or export manually from UI |
| GA4 | ✅ Reference | `Advanced SEO Analysis/clients/hogeye/outputs/ga4-findings.md` — organic engagement strong; blog → buy path worth linking |
| Screaming Frog | ✅ MCP in Hogeye repo | `docs/SCREAMING_FROG_MCP.md` + `workspace/technical_seo/`; comparison crawls after technical fixes |

---

## North Star check (all 5)

- [x] Remote hog trap monitoring angle on ops pieces (2, 3, 4)  
- [x] Trap closure / sounder capture on ops pieces  
- [x] Texas piece routes to systematic trapping + monitoring  
- [x] Field guide routes to cost/damage ROI (May post) and trapping response  

---

## After Schell approval

1. Merge `google_doc/` → `drafts/jun26_*_draft.md` → humanizer + QA → `content/posts/jun26_*_wp_draft.json`.
2. Push WordPress **draft only** (June publish window).
3. Run `PAGE_UPDATES_JUNE.md` hub work.
4. Bump `ARTICLE_PIPELINE_TRACKER.md` + `CONTENT_REGISTRY.md`.
