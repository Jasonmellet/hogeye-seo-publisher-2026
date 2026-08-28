# Monthly folders — what `YYYY-MM` and `mon26_NN` mean

## One rule

**`monthly/YYYY-MM/` and article IDs like `apr26_02` or `may26_03` refer to the target *publication* month (when the post is supposed to go live on the site), not:**

- the month you ran keyword research,
- the month you wrote the first draft,
- nor “today’s” calendar month while you are editing.

Research and drafting often happen **one or more months before** that publication window. Example: the **April 2026** trap-release batch (`apr26_01`–`apr26_05`) used **March 2026** DataForSEO and transcript work — see `content_pipeline/research/trap_release_20260318_210051Z/` and `research/2026-04-five-piece-blueprint.md`.

## Two batches you should not conflate

| Folder | IDs | Role |
|--------|-----|------|
| `2026-04/` | `apr26_01`–`apr26_05` | Trap monitor / trigger SOP series (March research → **April** go-live; see `CONTENT_REGISTRY.md`). |
| `2026-05/` | `may26_01`–`may26_05` | SEO “May package” — **published 2026-05-04**. |
| `2026-06/` | `jun26_01`–`jun26_05` | June publication batch — **sent to Schell 2026-05-19** ([`STATUS.md`](2026-06/STATUS.md)). |
| `2026-07/` | `jul26_01`–`jul26_05` | July batch — **live**; hub approved ([`READY_FOR_REVIEW.md`](2026-07/READY_FOR_REVIEW.md)). |
| `2026-08/` | `aug26_01`–`aug26_05` | August batch — 4/5 hub **approved**, WP **drafts** 500485–500488; `aug26_02` HOLD ([`READY_FOR_REVIEW.md`](2026-08/READY_FOR_REVIEW.md)). |
| `2026-09/` | `sep26_01`–`sep26_06` (5 active) | September batch — 5/5 hub **in_review**; overflow `sep26_04`, `07`–`10` parked ([`READY_FOR_REVIEW.md`](2026-09/READY_FOR_REVIEW.md)). |

If “it’s April now but we’re prepping May,” that is expected: you work in **`2026-05/`** for the **May** slot.

## Queue row `month` column

Matches the folder name (`2026-04`, `2026-05`, …) = publication batch. Optional notes can spell out `research: 2026-03` when helpful.

## See also

- [`../WORKFLOW.md`](../WORKFLOW.md) — pipeline stages  
- [`../../CONTENT_REGISTRY.md`](../../CONTENT_REGISTRY.md) — titles, slugs, status  
