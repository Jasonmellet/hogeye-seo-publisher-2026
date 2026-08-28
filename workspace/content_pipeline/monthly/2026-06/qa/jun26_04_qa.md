<!-- scaffolded_by: scripts/seo/hogeye_create_monthly_pipeline.py -->
<!-- month: 2026-06 -->
<!-- article_id: jun26_04 -->

# QA Checklist Template

## Article identity

- article_id:
- month:
- brief_path:
- research_pack_path:
- draft_path:

## Brand compliance checks

- [ ] Audience does not use banned term `ranchers`
- [ ] Product framing stays in approved wild hog trap monitor scope
- [ ] No drift into generic monitoring/surveillance/security language
- [ ] Tone and phrasing align with owner guidance

## Factual compliance checks

- [ ] Every substantive claim has a listed source
- [ ] No invented metrics
- [ ] No invented case studies or customer stories
- [ ] No unsupported performance or warranty claims
- [ ] Unsupported claims removed and logged

## SEO completeness checks

- [ ] Primary keyword used naturally
- [ ] Secondary keywords are relevant and non-spammy
- [ ] Search intent fully answered
- [ ] Internal links included from brief guidance
- [ ] Metadata block present and complete

## LLM discoverability checks

- [ ] Definitions are clear where needed
- [ ] Entity naming is consistent
- [ ] Headings are structured and specific
- [ ] Includes direct answers to likely user questions
- [ ] Language is concise, factual, and quotable

## Humanizer pass checks

- [ ] Final draft file exists (`<article_id>_draft.md`)
- [ ] Voice is more natural/conversational while staying professional
- [ ] Factual meaning is unchanged from source-backed draft
- [ ] No new claims were introduced during humanization
- [ ] Tone reflects TJ-style practical field guidance without slang overuse

## Validation checks

- [ ] Validator run completed
- [ ] No validator errors remain
- [ ] Any validator warnings were reviewed intentionally

## Post-flight: WordPress draft (before changing status to Publish)

Run this **after** `scripts/publisher/publish_content_item.py` has pushed a **draft** to WordPress and **before** you set the post to **Publish** (live).

- [ ] Open the post preview (or editor) and read the rendered article in the theme (headings, images, FAQ section).
- [ ] **AIOSEO:** SEO title, meta description, and focus keyphrase look correct; Schema shows **Article/BlogPosting** and **FAQ** (FAQPage) when applicable.
- [ ] **Links:** No raw `{{link:...}}` text in the body; internal links resolve to the intended HogEye URLs.
- [ ] **Taxonomy:** Categories and tags match the plan; slug is correct.
- [ ] **Brand/truth:** Quick pass—no banned audience terms or off-positioning framing (`brand_truth/` rules).
- [ ] Optional: Rich Results Test or view source on the URL **after** go-live (preview URLs can differ from final).

## Required data use checks

- [ ] DataForSEO evidence is present
- [ ] GSC data used where relevant
- [ ] GA4 data used where relevant

## Excluded unsupported claims

- item:
  - reason:
  - missing source:

## QA result

- status: PASS or FAIL
- blockers:
- fixes required:
- reviewed_by:
- reviewed_at:
