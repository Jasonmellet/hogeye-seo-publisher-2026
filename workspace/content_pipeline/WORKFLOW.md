# HogEye Phase-1 Content Pipeline

This workflow is for SEO and LLM discovery content generation only.

It ends at review handoff and does not auto-publish to WordPress.

## Outcome

Each monthly run produces 5-10 article packages where every draft has:

- a brief
- a research pack
- a **final** `drafts/<article_id>_draft.md` (metadata + body; voice-checked before you see it)
- a QA report
- a Google Docs handoff entry (optional)

## Pipeline stages

0. Source ingestion and knowledge-base refresh
1. Data refresh (required before queue finalization)
2. Monthly queue creation
3. Brief creation
4. Research pack creation
5. Draft writing (scaffold from template, then replace with final copy)
6. Voice / readability pass (fact-locked; no new claims)
7. QA and compliance checks
8. Google Docs review handoff

## WordPress taxonomy (before Phase 2 publish)

Categories and tags are **not** chosen by automation. The SEO/content owner maps each article to **existing** WordPress categories (and tags, if used) so URLs, archives, and internal linking stay intentional.

- Confirm category names against **WP Admin → Posts → Categories**, or run `./.venv/bin/python scripts/seo/hogeye_wp_list_taxonomy.py` (uses `WP_*` in `.env`; prints decoded names for copy-paste).
- Record per article in the draft file **Metadata** as `- categories: Name` (and optionally `- tags: …`), **or** set repeatable defaults in `PROJECT_CONFIG.json` → `wordpress.default_post_categories` / `default_post_tags` only after strategy is locked.
- The md → JSON bridge (`hogeye_draft_md_to_post_json.py`) **requires** at least one category (from config defaults and/or draft lines).

## Source ingestion and knowledge base

Before planning a new piece, ingest any high-value source material that should improve future writing quality:

- videos: `npm run transcribe -- --auto <media-path>`
- website copy / article files: `npm run ingest-source -- <file-path>`

New Theo-style source artifacts live in:

- `workspace/content_pipeline/sources/media_inbox/`
- `workspace/content_pipeline/sources/source_notes/`
- `workspace/content_pipeline/sources/transcripts/raw/`
- `workspace/content_pipeline/sources/transcripts/processed/`
- `workspace/content_pipeline/sources/derived_notes/`

Derived notes are preferred for transcript-backed content, but they do not replace research pack evidence.

## Data refresh requirements

DataForSEO is mandatory.

Use existing scripts:

- `scripts/seo/dataforseo_benchmark_rank_snapshot.py`
- `scripts/seo/hogeye_ranch_camera_keyword_analysis.py` (or `scripts/seo/hogeye_trap_release_keyword_analysis.py`)

Add GSC and GA4 overlays when available:

- `scripts/seo/gsc_benchmark_pull.py`
- `scripts/seo/ga4_benchmark_pull.py`

Reference existing outputs:

- `work/seo/benchmark/YYYY-MM-DD/`
- `work/seo/plan/`
- `workspace/keyword_analysis/`

## Content package requirements

**`YYYY-MM` in `monthly/YYYY-MM` is the target *publication* month** (go-live on the site), not “the month we did keyword research.” Research can run earlier (e.g. March research for an April publication batch). See [`monthly/README.md`](monthly/README.md).

Each article package in `monthly/YYYY-MM` must include:

- `briefs/<article_id>_brief.md`
- `research_packs/<article_id>_research_pack.md`
- `drafts/<article_id>_draft.md` (single final markdown per article)
- `qa/<article_id>_qa.md`

Each **final draft** must include a **LLM-friendly FAQ**: H2 **`Frequently Asked Questions`**, a one-line intro, and **at least five** H3 Q&As with self-contained answers. Add **internal links** using `{{link:alias|anchor}}` placeholders (aliases from `client.config.json`); resolve them at publish with `scripts/publisher/publish_content_item.py --resolve-links`.

No draft proceeds to handoff unless the QA checklist passes.
Run validator checks before treating an article package as approval-ready:

- `npm run validate-artifact -- <artifact-path>`

## Brand and truth gates

Before drafting and in QA:

- enforce `workspace/brand_truth/OWNER_RULES_OVERRIDE.md`
- enforce `workspace/brand_truth/APPROVED_LANGUAGE.yml`
- enforce `workspace/brand_truth/TRUTH_HIERARCHY.md`
- enforce `workspace/NORTH_STAR_POSITIONING.md`
- enforce `workspace/KEYWORD_BLACKLIST.md`

If a claim cannot be supported by approved sources, remove the claim and list it in `excluded unsupported claims`.

## Monthly operator sequence

1. Refresh benchmark and keyword datasets.
2. Populate `queue/monthly_queue.csv` with 5-10 targets.
3. Create briefs from template.
4. Build research packs from template with source evidence and any relevant derived notes.
5. Write drafts from template with metadata block.
6. Run voice pass using `HUMANIZER_STYLE_GUIDE.md` and `templates/humanizer_pass.template.md` (fact-locked readability; **no em dashes**; normal punctuation; see guide).
7. Run validator + QA template and fail anything with banned wording, unsupported claims, or fact drift introduced in editing.
8. Prepare handoff packet for Google Docs review.

## LLM discoverability quality targets

Drafts should include:

- clear definitions where needed
- explicit entity naming and consistent terminology
- direct answers to likely user questions
- structured headings and concise sections
- factual, non-fluffy language suitable for citation and quoting

## Phase-2 hook (WordPress draft publishing)

When phase 2 starts, approved drafts can move to WordPress draft staging through:

- `scripts/publisher/publish_content_item.py` (single item, draft-first; use `--resolve-links` for internal links)
- `scripts/publisher/publish_batch.py` (batch, draft-first)

This phase-1 workflow document describes content packages; WordPress pushes are **draft-first** until you explicitly publish.

### Post-flight (before live Publish)

After the draft exists in WordPress, complete the **Post-flight: WordPress draft** checklist in `templates/qa_checklist.template.md` (same section should appear in each month’s `qa/<article_id>_qa.md`). Only then change the post status from **Draft** to **Publish**. This catches theme rendering, AIOSEO schema, unresolved link placeholders, and taxonomy issues while the URL is still non-public.
