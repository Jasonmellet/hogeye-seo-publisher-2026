# HogEye Phase 2 WordPress Draft Bridge

Bridge from phase-1 approved content packages into WordPress **draft** creation using the existing Python publisher.

## Entry criteria

Only artifacts that meet all of the following should be eligible:

- brief completed
- research pack completed
- final draft completed (`drafts/<article_id>_draft.md`)
- QA marked PASS
- client or internal approval status recorded outside the draft body

## Bridge strategy

Reuse existing Python WordPress tooling instead of duplicating a second publishing stack:

- [`scripts/publisher/publish_content_item.py`](../../../../scripts/publisher/publish_content_item.py) (canonical)
- [`scripts/publisher/publish_batch.py`](../../../../scripts/publisher/publish_batch.py)
- Optional: [`scripts/seo/hogeye_publish_draft_post_with_aioseo.py`](../../../../scripts/seo/hogeye_publish_draft_post_with_aioseo.py)

## Transform: draft markdown → post JSON

Deterministic helper (no WordPress write):

```bash
./.venv/bin/python scripts/seo/hogeye_draft_md_to_post_json.py \
  workspace/content_pipeline/monthly/2026-04/drafts/apr26_01_draft.md \
  --output content/posts/apr26_01_wp_draft.json
```

Then push a **draft** (after `scripts/publisher/test_connection.py` and `client.config.json` match HogEye):

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py content/posts/apr26_01_wp_draft.json --type posts --status draft
```

Optional: `--slug my-custom-slug` if you do not want the default slugify-from-title behavior.

Use `--resolve-links` when the JSON or draft used `{{link:...}}` placeholders.

The script strips HTML comment blocks, skips `# Draft: …` scaffolding, uses the first real `# Title` as the article start, drops `## Claims audit notes` from the HTML body by default, and fills `meta_title`, `meta_description`, `focus_keyword` from the SEO/Metadata bullet lists. **Categories and tags** are decided by the SEO/content owner (see `content_pipeline/WORKFLOW.md`): merged from optional `PROJECT_CONFIG.json` defaults and per-draft `- categories:` / `- tags:` lines; at least one category is required (no generic auto-category).

## Post-flight (before Publish)

After the draft exists in WordPress, complete the **Post-flight: WordPress draft** checklist in `content_pipeline/templates/qa_checklist.template.md` (and in that article’s `qa/<article_id>_qa.md`). Only then change status from **Draft** to **Publish**. See `content_pipeline/WORKFLOW.md` → Phase-2 hook → Post-flight.

## Out of scope

- live publish
- auto-publish on approval
- bypassing WordPress draft review
