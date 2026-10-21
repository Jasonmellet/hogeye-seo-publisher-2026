# Thread: September writing-skill remediation

- Date: 2026-09-27
- Agent: Cursor
- Status: ready-to-archive

## Goal

Add a fail-closed editorial gate for style, taste, flow, reader effort, and
enjoyment, then remediate the five active September V2 posts.

## Decisions

- Facts, SEO, length, and Flesch are necessary but cannot grant readiness.
- Every new article begins with a validated 35–60 word TL;DR.
- Preserve HogEye's practical observation voice while rejecting mechanical or
  research-note-shaped prose.
- Preserve V1 and re-push corrected copy under the existing V2 identities.

## Changes

- `scripts/editorial-gate.mjs` — shared TypeSafe Jev editorial review.
- `workspace/content_system/prompts/system/hogeye_writer_system_prompt.md` —
  explicit writing-skill and editorial failure contract.
- `scripts/content-system/agent_batch_review.ts` — style/taste is a gate.
- `scripts/push-content.mjs` — fail closed on the editorial gate.

## Verification

- Typecheck and syntax checks pass.
- Existing September V2 copy triggers the new editorial gate.
- Rewritten pilot `sep26_03-v2` passes native quality and editorial gates.
- All five September V2 posts now include TL;DR blocks and pass the native and
  editorial gates.
- All five existing V2 identities were re-pushed to the Hub without changing V1
  or duplicating images.

## Open questions

- Pilot copy requires human acceptance before scaling to the remaining batch.

## Archive summary

HogEye now requires a separate editorial style/taste decision before Hub ingest
instead of treating mechanical content checks as sufficient.
