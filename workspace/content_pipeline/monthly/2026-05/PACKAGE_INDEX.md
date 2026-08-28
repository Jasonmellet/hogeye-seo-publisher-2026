# May 2026 Content Package — HogEye

**Theme:** Problem Awareness + Trap Operations Foundation  
**Status:** Briefs + first-pass drafts live in this month folder (`drafts/may26_0X_draft.md`).  
**Canonical tree:** `workspace/content_pipeline/monthly/2026-05/` (also visible as `output/drafts/2026-05/`).  
**Strategy doc:** `workspace/SEO_STRATEGY_MAY_JUL_2026.md`  
**Client review (Google comments):** [Hog Eye | 2026 SEO Strategy & Blueprint](https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit) — `file_id` `1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y`. Traceability table: `workspace/CONTENT_REGISTRY.md` → section *Google Doc ↔ repository*. Per-article handoffs: `handoff/may26_*_handoff.md`.

---

## New Content Briefs (5 pieces)

| #   | Brief (canonical path)     | Title                                                  | Primary KW                           | Volume         | Priority    |
| --- | -------------------------- | ------------------------------------------------------ | ------------------------------------ | -------------- | ----------- |
| 1   | `briefs/may26_01_brief.md` | How Much Do Feral Hogs Cost You?                       | feral hog damage                     | 170/mo         | High        |
| 2   | `briefs/may26_02_brief.md` | Wild Hog Behavior: Movement, Scouting, and Trap Timing | wild hog behavior / wild hog hunting | 8,100/mo entry | High        |
| 3   | `briefs/may26_03_brief.md` | The Hog Trap Baiting Guide                             | wild hog bait                        | 260/mo         | High        |
| 4   | `briefs/may26_04_brief.md` | Common Hog Trap Mistakes                               | hog trapping techniques              | —              | High        |
| 5   | `briefs/may26_05_brief.md` | Corral vs. Box vs. Drop Net                            | corral hog trap                      | 590/mo         | **Highest** |

**Recommended draft order:** 5 → 4 → 3 → 2 → 1  
(Trap comparison is the highest-gap piece. Mistakes and baiting support each other. Behavior and damage are broader entry points.)

---

## Page Updates (5 targets)

| Page                                                       | Update Focus                                                                                  |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `/trap-camera/`                                            | Add FAQ schema: "How often should I check my hog trap?", "What are common hog trap mistakes?" |
| `/steel-camera/`                                           | Add FAQ schema around reliability and trigger latency                                         |
| `/net-camera-trap/`                                        | Add comparison context linking to Brief 05 once live                                          |
| `/camera-resources/`                                       | Add baiting + placement content as internal link targets after May pieces publish             |
| `/reolink-vs-vosker-vs-hogeye-off-grid-camera-comparison/` | Reframe around trap outcomes (flagged in April planning)                                      |

---

## Internal Linking Map (once all 5 pieces are live)

```
Brief 01 (damage cost)
  └── links to: Brief 04 (mistakes), Brief 05 (trap types), /trap-camera/

Brief 02 (behavior)
  └── links to: Brief 03 (baiting), Brief 04 (mistakes), /trap-camera/

Brief 03 (baiting)
  └── links to: Brief 02 (behavior), Brief 04 (mistakes), /trap-camera/

Brief 04 (mistakes)
  └── links to: Brief 02 (behavior), Brief 03 (baiting), Brief 05 (trap types), /trap-camera/

Brief 05 (trap comparison)
  └── links to: Brief 02 (behavior), Brief 03 (baiting), Brief 04 (mistakes), /trap-camera/, /steel-camera/, /net-camera-trap/
```

---

## North Star Check (all 5 pieces)

Every piece routes to one or more of:
- [x] How does this help remote hog trap monitoring? (Briefs 02, 03, 04, 05)
- [x] How does this improve trap closure timing? (Briefs 02, 03, 04)
- [x] How does this improve sounder capture outcomes? (Briefs 02, 04, 05)
- [x] How does this reduce wasted trips or missed captures? (Briefs 03, 04)

Brief 01 (damage cost) is the entry-point piece — it establishes the problem. The North Star connection is the ROI conclusion section.

---

## Research Files Used

All outputs in `work/seo/plan/`:
- `hogeye_keyword_gap_combined.csv` — keyword gap source
- `hogeye_paa_questions.csv` — PAA questions used in briefs
- `hogeye_keywords_for_site.csv` — existing HogEye keyword universe
