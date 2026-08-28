# HogEye Content Publisher — Project Status

**Last updated:** 2026-08-24  
**Client:** HogEye Cameras (Schell approval workflow)  
**Hub slug:** `hogeye-cameras`  
**Monthly playbook:** [`MONTHLY_PUBLISHING_WORKFLOW.md`](MONTHLY_PUBLISHING_WORKFLOW.md)

---

## Current gate

| Period | Hub | WordPress | Blocker |
| ------ | --- | --------- | ------- |
| July 2026 (`jul26_01`–`05`) | 5/5 approved | **Live** | `jul26_01` local/hub content drift. Do not overwrite live URLs unless ordered. |
| August 2026 (`aug26_01`, `03`, `04`, `05`) | 4/5 approved, images on hub | **WP drafts** 500485–500488 | Schell done on hub. Lily publishes from WordPress when go-live is ordered. |
| September 2026 (`sep26_01`–`03`, `05`, `06`) | 5/5 in_review | not in WP | Schell hub copy review. Overflow parked repo-local (not on hub Oct tab). |
| `aug26_02` Mini Starlink | Not on hub | HOLD | Price / buy path (do not invent). |

Hub Approved ≠ live. August is in **WordPress drafts**. September is **in_review on hub**. Status email **sent** 2026-08-24. Say **publish August live** when ready.

Review indexes:

- [`workspace/content_pipeline/monthly/2026-07/READY_FOR_REVIEW.md`](../workspace/content_pipeline/monthly/2026-07/READY_FOR_REVIEW.md)
- [`workspace/content_pipeline/monthly/2026-08/READY_FOR_REVIEW.md`](../workspace/content_pipeline/monthly/2026-08/READY_FOR_REVIEW.md)
- [`workspace/content_pipeline/monthly/2026-09/READY_FOR_REVIEW.md`](../workspace/content_pipeline/monthly/2026-09/READY_FOR_REVIEW.md)

---

## Current focus: August 2026 publish pipeline

**August plan:** [`workspace/content_pipeline/monthly/2026-08/CONTENT_PLAN.md`](../workspace/content_pipeline/monthly/2026-08/CONTENT_PLAN.md)

| Milestone | Status |
| --- | --- |
| July 2026 batch (5 posts) | ✅ Live on hogeyecameras.com |
| August drafts + hub push (4 posts) | ✅ Approved in hub 2026-08-21 |
| August WP drafts | ✅ 500485–500488 (draft, not live) |
| `aug26_02` Starlink | ⏳ HOLD |
| September slate (5 posts) | ✅ In review on hub 2026-08-24 (5 parked for Oct+) |

---

## Operational trackers

| Doc | Purpose |
| --- | --- |
| [`workspace/EXECUTION_STATUS.md`](../workspace/EXECUTION_STATUS.md) | Phase checklist (may lag hub; Current gate above wins) |
| [`workspace/ARTICLE_PIPELINE_TRACKER.md`](../workspace/ARTICLE_PIPELINE_TRACKER.md) | Pipeline stage per `article_id` |
| [`workspace/CONTENT_REGISTRY.md`](../workspace/CONTENT_REGISTRY.md) | Titles, slugs, keywords, link map |
| [`workspace/content_pipeline/research/README.md`](../workspace/content_pipeline/research/README.md) | Research bundle index |

---

## Strategy docs

| Doc | Notes |
| --- | ----- |
| `SEO_STRATEGY.md` | Portal Strategy tab (**V2**, pushed 2026-08-24) |
| `workspace/brand_truth/BRAND_BASELINE.md` | Portal Overview tab |
| `workspace/SEO_STRATEGY_JUL_DEC_2026.md` | Internal Jul–Dec roadmap |
| `sprint_20260622_audit/findings/content-strategy-opportunities.md` | Jul–Dec opportunity stack |

---

## Immediate ops (from June SF crawl)

1. **`/trap-camera/`** 404 → redirect `/steel-camera/` (128+ GSC clicks)
2. H1/meta template pass (50% HTML missing H1)
3. `/buy-now/` depth + GA4 revenue tagging
4. Restore 404 blog slugs linked from live posts

Details: `sprint_20260622_audit/findings/technical-findings.md`

---

## See also

- Agent skill: [`.cursor/skills/he-monthly-cycle/SKILL.md`](../.cursor/skills/he-monthly-cycle/SKILL.md)
- Operator runbook: [`starter.md`](starter.md)
- Monthly folder convention: [`../workspace/content_pipeline/monthly/README.md`](../workspace/content_pipeline/monthly/README.md)
