# HogEye Truth Hierarchy for Content Generation

This hierarchy governs briefs, research packs, drafts, and QA decisions.

**Start here:** `workspace/brand_truth/BRAND_BASELINE.md` — orientation layer (brand truth, verified facts, vocabulary, workflows) before diving into individual rule files.

## Source priority (highest to lowest)

1. Client website (primary truth for product naming, positioning, terminology, and offer framing)
2. Approved internal docs in this repo
3. Google Docs / Google Sheets strategy materials
4. DataForSEO data
5. Google Search Console data
6. GA4 data
7. Carefully selected external sources only when needed for non-promotional factual statements

## Non-negotiable rules

- Never invent facts.
- Never invent use cases.
- Never invent performance metrics.
- Never invent case studies.
- Never invent fictional customer stories.
- Never leave placeholder facts as final facts.
- If supporting data is missing, skip the claim.

## Website-as-truth rule

Start from the official website for:

- product naming
- positioning
- approved use case framing
- terminology
- value proposition framing

If older website wording conflicts with newer owner feedback, owner feedback in `OWNER_RULES_OVERRIDE.md` overrides older wording for all generated content.

## Verification standard per article

Each draft must include:

- source list with file links or dataset references
- explicit unsupported/excluded claims list
- statement of approved positioning used
- QA check confirmation that banned language was not used
