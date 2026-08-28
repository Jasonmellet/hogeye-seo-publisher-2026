<!-- article_id: jul26_01 -->
<!-- month: 2026-07 -->

# QA — What Is New World Screwworm?

## Article identity

- article_id: jul26_01
- month: 2026-07
- brief_path: workspace/content_pipeline/monthly/2026-07/briefs/jul26_01_brief.md
- research_pack_path: workspace/content_pipeline/monthly/2026-07/research_packs/jul26_01_research_pack.md
- draft_path: workspace/content_pipeline/monthly/2026-07/drafts/jul26_01_draft.md

## Brand compliance checks

- [x] Audience does not use banned term `ranchers`
- [x] Product framing stays in approved wild hog trap monitor scope
- [x] No drift into generic monitoring/surveillance/security language
- [x] Tone and phrasing align with owner guidance

## Factual compliance checks

- [x] Every substantive claim has a listed source
- [x] No invented metrics
- [x] No invented case studies or customer stories
- [x] No unsupported performance or warranty claims
- [x] Unsupported claims removed and logged (outbreak dates/case counts excluded)

## SEO completeness checks

- [x] Primary keyword used naturally ("what is screwworm")
- [x] Secondary keywords are relevant and non-spammy
- [x] Search intent fully answered (definition + spread + why it matters)
- [x] Internal links included from brief guidance (/trap-camera/, /steel-camera/, /camera-resources/, /buy-now/)
- [x] Metadata block present and complete (frontmatter: meta_title, meta_description, focus_keyword, slug)

## LLM discoverability checks

- [x] Definitions are clear where needed
- [x] Entity naming is consistent (New World screwworm / USDA APHIS)
- [x] Headings are structured and specific
- [x] Includes direct answers to likely user questions (5 FAQ)
- [x] Language is concise, factual, and quotable

## Humanizer pass checks

- [x] Final draft file exists (`jul26_01_draft.md`)
- [x] Voice is natural/conversational while staying professional
- [x] Factual meaning is unchanged from source-backed draft
- [x] No new claims were introduced during humanization
- [x] Tone reflects practical field guidance without slang overuse

## Validation checks

- [x] Validator run completed (brief + research_pack pass `validate-artifact`)
- [x] No validator errors remain on brief/research pack
- [x] Content lint passed: no em dashes, no banned terms, FAQ schema clean (5 items), JSON generated via md→JSON bridge

## Post-flight: WordPress draft (before changing status to Publish)

Run after the post is pushed as a WordPress draft and BEFORE setting Publish. NOTE: per the approval gate, publish only after the post is Approved in the Wildlife Dominion dashboard.

- [ ] Open the post preview and read the rendered article (headings, FAQ section)
- [ ] AIOSEO: SEO title, meta description, focus keyphrase correct; Article + FAQ schema present
- [ ] Links: no raw `{{link:...}}`; internal links resolve to intended HogEye URLs
- [ ] Taxonomy: category "Feral Hog Educational & Awareness"; slug `what-is-new-world-screwworm`
- [ ] Brand/truth: no banned audience terms or off-positioning framing

## Required data use checks

- [x] DataForSEO evidence is present
- [x] GSC data used where relevant (screwworm greenfield confirmed)
- [ ] GA4 data used where relevant (not applicable to this article)

## Excluded unsupported claims

- item: specific NWS outbreak dates, locations, case counts
  - reason: not verifiable from repo sources
  - missing source: dated USDA APHIS situation reports

## QA result

- status: PASS
- blockers: none
- fixes required: Body word count ~1,190 (under the 1,400-2,000 house target) — reviewer to decide if expansion is needed before publish.
- reviewed_by: AGT content pipeline (automated pre-review); pending Schell approval in dashboard
- reviewed_at: 2026-06-25
