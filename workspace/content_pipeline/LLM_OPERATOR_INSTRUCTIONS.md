# HogEye LLM Operator Instructions

Use this file when generating SEO blog drafts for HogEye.

**Read first:** `workspace/brand_truth/BRAND_BASELINE.md`

## Mission scope

- Generate blog draft packages for organic and LLM discovery traffic.
- Do not produce paid media, social assets, or broad campaign content.

## Hard constraints

1. Never refer to audience as `ranchers`.
2. Keep product framing in approved wild hog trap monitor language only.
3. Never broaden framing to surveillance, property monitoring, or general security.
4. Never invent facts, claims, metrics, stories, or case studies.
5. If support is missing, omit the claim.

## Required sources and order

Use this hierarchy:

1. HogEye website
2. Approved internal docs in this repo
3. Google Docs / Google Sheets strategy materials
4. DataForSEO data
5. GSC data
6. GA4 data
7. External sources only when necessary for non-promotional facts

## Mandatory workflow

1. Confirm target topic exists in monthly queue.
2. Ingest any net-new high-value source material before drafting:
   - `npm run transcribe -- --auto <media-path>`
   - `npm run ingest-source -- <file-path>`
3. Build brief from template.
4. Build research pack from template with source support and derived notes where relevant.
5. Draft article using approved language and metadata block.
6. Run a fact-locked humanizer pass using `HUMANIZER_STYLE_GUIDE.md`.
7. Run validator and QA checklist.
8. Before WordPress publish (Phase 2): assign **categories and tags** that match live WP taxonomy — add `- categories:` / `- tags:` to draft Metadata and/or set `PROJECT_CONFIG.json` defaults only after SEO locks them (see `WORKFLOW.md`).
9. Prepare Google Docs handoff record.

Do not skip research pack or QA.
Do not let humanizer edits change factual meaning.

## LLM-friendly FAQ and internal links (required before publish)

Every final draft must include:

1. **FAQ block** — Use the H2 title **`Frequently Asked Questions`** (not `FAQ` alone) so validators and parsers can find the section. Include **at least five** H3 questions with **self-contained answers** (each answer should make sense without the rest of the article). Add one short line under the H2 explaining the section is for quick scanning and assistants.

2. **Internal links** — Add **at least three** `{{link:alias|anchor text}}` placeholders to the body or FAQ using keys from `client.config.json` → `linkAliases` (for example `camera_resources`, `net_trap_camera`, `trap_camera`, `blog`, `buy_now`). At publish, run `scripts/publisher/publish_content_item.py` with **`--resolve-links`** so placeholders become real `<a href>` tags.

3. **FAQ schema (AIOSEO)** — The md → JSON bridge fills `faq_items` from the **Frequently Asked Questions** section. On publish, the pipeline sends an **AIOSEO `FAQPage` graph** in `aioseo_meta_data.schema` so the Schema panel shows FAQ alongside **Article/BlogPosting**, not body HTML alone.

## Required references

- `workspace/brand_truth/OWNER_RULES_OVERRIDE.md`
- `workspace/brand_truth/APPROVED_LANGUAGE.yml`
- `workspace/brand_truth/TRUTH_HIERARCHY.md`
- `workspace/NORTH_STAR_POSITIONING.md`
- `workspace/content_pipeline/WORKFLOW.md`
- `workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`
- `workspace/content_system/config/evidence_and_truth.md`
- `workspace/content_system/config/artifact_contract.md`

## Data requirement

DataForSEO evidence is required for planning and research.

GSC and GA4 should be used where relevant and available.
