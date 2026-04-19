# HogEye Artifact Contract

The Theo-style runtime plugs into the existing HogEye monthly package structure.

## Canonical stage artifacts

- `sources/source_notes/`: normalized text inputs from articles, website copy, and manual source drops
- `sources/transcripts/raw/`: raw transcript API outputs and intermediate raw text
- `sources/transcripts/processed/`: markdown transcripts with provenance frontmatter
- `sources/derived_notes/`: structured editorial notes generated from transcripts
- `monthly/YYYY-MM/briefs/*_brief.md`
- `monthly/YYYY-MM/research_packs/*_research_pack.md`
- `monthly/YYYY-MM/drafts/*_draft.md`
- `monthly/YYYY-MM/drafts/<article_id>_draft.md`
- `monthly/YYYY-MM/qa/*_qa.md`
- `monthly/YYYY-MM/handoff/*_handoff.md`

## Validation expectations

### Briefs
- must define keyword target
- must define approved audience and positioning
- must name DataForSEO source input

### Research packs
- must lock approved positioning
- must include website truth
- must include DataForSEO evidence
- must include excluded unsupported claims

### Drafts (final monthly markdown)
- must include metadata block
- must name approved positioning angle
- must preserve source-backed claims only

### QA
- must include PASS/FAIL status
- must confirm banned framing checks
- must confirm factual compliance

## Compatibility rule

New tooling must validate the existing HogEye artifact format before introducing more rigid frontmatter contracts.
