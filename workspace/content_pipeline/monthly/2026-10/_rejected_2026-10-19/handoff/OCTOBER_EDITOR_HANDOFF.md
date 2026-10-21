# Editor handoff — HogEye October 2026

**Date:** 2026-10-16  
**Period:** `2026-10`  
**Hub brand:** `hogeye-cameras`  
**Your job:** Fact-check and edit these five local drafts. Do not push to the hub. Do not publish to WordPress. Do not pull or apply September.

You are the HogEye Chief Editor. Final editorial authority before client review. Return one verdict per piece: APPROVED, APPROVED WITH REQUIRED FIXES, NEEDS REVISION, or BLOCKED. Quote the text that must change. Do not invent a missing fact. If a number, competitor spec, bait claim, or Alabama rule is not already sourced, mark it `[NEEDS SOURCE]` in your verdict, not as a new claim in the article. The local quality gate fails on that token, so do not leave it in the body unless Jason asks for a failing draft.

## Where the content is

Edit the markdown. The JSON is what the quality gate and a later hub push read. After you change a draft, regenerate its JSON. Do not edit September files.

| ID | Markdown (edit this) | JSON (regenerate after edits) |
| -- | -------------------- | ------------------------------ |
| oct26_01 | `workspace/content_pipeline/monthly/2026-10/drafts/oct26_01_draft.md` | `content/posts/oct26_01_wp_draft.json` |
| oct26_02 | `workspace/content_pipeline/monthly/2026-10/drafts/oct26_02_draft.md` | `content/posts/oct26_02_wp_draft.json` |
| oct26_03 | `workspace/content_pipeline/monthly/2026-10/drafts/oct26_03_draft.md` | `content/posts/oct26_03_wp_draft.json` |
| oct26_04 | `workspace/content_pipeline/monthly/2026-10/drafts/oct26_04_draft.md` | `content/posts/oct26_04_wp_draft.json` |
| oct26_05 | `workspace/content_pipeline/monthly/2026-10/drafts/oct26_05_draft.md` | `content/posts/oct26_05_wp_draft.json` |

`content/posts/` and `output/wordpress/posts/` are the same files. A save in one path changes the other.

Status board: `workspace/content_pipeline/monthly/2026-10/READY_FOR_REVIEW.md`

Regenerate one JSON file from the repo root:

```bash
./.venv/bin/python scripts/seo/hogeye_draft_md_to_post_json.py \
  workspace/content_pipeline/monthly/2026-10/drafts/oct26_01_draft.md \
  --output content/posts/oct26_01_wp_draft.json
```

Then put `"period": "2026-10"` back on the JSON if the converter drops it. Re-run:

```bash
./.venv/bin/python scripts/seo/hogeye_content_quality.py \
  content/posts/oct26_01_wp_draft.json \
  content/posts/oct26_02_wp_draft.json \
  content/posts/oct26_03_wp_draft.json \
  content/posts/oct26_04_wp_draft.json \
  content/posts/oct26_05_wp_draft.json
```

The gate already passed on 2026-10-16 at 800 words, band 760–840: oct26_01 825, oct26_02 822, oct26_03 832, oct26_04 829, oct26_05 834. Stay inside that band.

## Read before you edit

1. `workspace/brand_truth/BRAND_BASELINE.md`
2. `workspace/PRE_SUBMISSION_QA_CHECKLIST.md`
3. `workspace/CLIENT_FEEDBACK_SCHELL_APR2026.md`
4. `workspace/HOGEYE_CONTENT_STYLE_GUIDE.md`
5. `workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`
6. `docs/agents/AGENT_CHIEF_EDITOR.md`

Voice: landowners, land managers, trappers. Never ranchers. No security or surveillance framing. No em dashes. No unreleased Mini AI or Mini Starlink. HogEye Mini is $1,299. Data plan is $49.99 per month on AT&T or Verizon, no contract. Three-year bumper-to-bumper replacement warranty. About 75% smaller and about 60% less power than legacy, with a compact battery and small solar panel. Those figures come from the brand baseline, not from a new source you need to invent.

Each body opens with one `TL;DR:` paragraph for Schell. Keep it. The publisher strips that first paragraph before WordPress. The TL;DR should stay about 35–60 words and should not add a new fact.

## The five pieces

1. **oct26_01.** Hog bait that deer won't eat. The camera shows who is on the bait. Do not add a bait recipe. Do not link a second bait-guide URL. Any bait claim needs a cited source.
2. **oct26_02.** Query `hog cam`. Definition only. It must link to `https://hogeyecameras.com/steel-camera/`. Do not rewrite the homepage. The camera does not close a gate by itself.
3. **oct26_03.** Query `barn owl hog trap camera`. Starting copy was parked `workspace/content_pipeline/monthly/2026-09/parked/sep26_04_wp_draft.json`. Do not reuse external ID `sep26_04`. Competitor specs, prices, and performance claims need a cited source. They were omitted on purpose.
4. **oct26_04.** Query `alabama hog trap monitoring`. Starting copy was parked `workspace/content_pipeline/monthly/2026-09/parked/sep26_07_wp_draft.json`. Do not reuse external ID `sep26_07`. Season, license, and method rules need a cited Alabama source. They were omitted on purpose. There is no new Texas monitoring article in this set.
5. **oct26_05.** Query `count hogs on trail camera`. Do not claim the camera closes a gate by itself. The singular phrase "trail camera" is banned in reader-facing fields by `scripts/seo/hogeye_content_quality.py`. Keep it in `focus_keyword` and the slug only, unless that gate changes.

No new screwworm post.

## Do not touch

September approved posts and these external IDs: `sep26_01`, `sep26_01-v2`, `sep26_02`, `sep26_02-v2`, `sep26_03`, `sep26_03-v2`, `sep26_05`, `sep26_05-v2`, `sep26_06`, `sep26_06-v2`.

Do not run `npm run push:content`, `scripts/pull-approved.mjs`, or any WordPress publish command.

Schell reviews these October rows only after this edit, and only after the new October rows are pushed.
