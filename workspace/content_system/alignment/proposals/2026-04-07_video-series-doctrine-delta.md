# HogEye Video Series Doctrine Delta (Videos 1-5)

- Date: 2026-04-07
- Scope: synthesis from five newly ingested transcript-derived note artifacts
- Purpose: tighten reusable language, messaging, and operational guidance for future briefs/drafts

## Source set reviewed

- `workspace/content_pipeline/sources/derived_notes/20260407T185546Z_20240610-system-unboxing-hogeye-legacy-camera-transcript.md`
- `workspace/content_pipeline/sources/derived_notes/20260407T191752Z_4-lzfycsa6s-transcript.md`
- `workspace/content_pipeline/sources/derived_notes/20260407T191838Z_wmdwyqt52k-transcript.md`
- `workspace/content_pipeline/sources/derived_notes/20260407T191925Z_ics-gvh91d8-transcript.md`
- `workspace/content_pipeline/sources/derived_notes/20260407T192003Z_w33wxftb9hw-transcript.md`

## What is clearly consistent across sources

1. Setup confidence depends on connection integrity checks.
   - recurring patterns: power light, strength light, carrier light, cable connection checks, latch-power confirmation
2. Trigger reliability is operational, not magic.
   - recurring patterns: secure gate-cable/latch connections, correct splitter direction, test trigger behavior
3. Antenna strategy materially affects trap outcomes.
   - recurring patterns: mount height, topography constraints, extension cable options, directional antenna edge cases
4. Field handling quality is part of system performance.
   - recurring patterns: transport care, cable damage prevention, careful dome reassembly, alignment before forcing parts
5. Operator language is practical and procedural.
   - recurring style: short direct instructions, if-then troubleshooting logic, clear setup sequence wording

## Messaging updates recommended (proposal)

## Add / strengthen

- Add stronger "connection integrity" language as a first-class reliability pillar in briefs and drafts.
- Strengthen setup SOP wording around:
  - indicator-light interpretation
  - cable/latch troubleshooting
  - pre-departure test behavior
- Strengthen antenna guidance as "trap execution reliability support" rather than generic connectivity tips.
- Reuse concise field phrases where helpful:
  - "plug and play"
  - "green to green"
  - "drop button"
  - "height is your friend for cell service"

## Reconcile

- Standardize product casing and naming to `HogEye` in all generated artifacts.
- Preserve North Star framing while using practical setup language from the videos.

## Remove / avoid

- Avoid broad technical claims without support in approved docs:
  - exact range ceilings
  - warranty details not already validated
  - blanket compatibility statements beyond confirmed models/specs

## Confidence map

- High confidence:
  - setup sequence logic
  - cable/connection troubleshooting flow
  - practical mounting and handling guidance
- Medium confidence (safe with careful wording):
  - directional antenna use-case positioning
  - statements about expected connectivity improvements from added height
- Low confidence (defer unless confirmed):
  - exact mileage/range outcomes
  - non-core component warranty specifics
  - quantifiable performance percentages

## Suggested downstream updates

- Target files for selective strengthening:
  - `workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`
  - `workspace/content_pipeline/templates/research_pack.template.md`
  - `workspace/content_pipeline/templates/draft.template.md`
  - `workspace/content_system/prompts/workflow/draft_article.md`

No direct changes are applied in this proposal file. This is a review-first alignment draft.
