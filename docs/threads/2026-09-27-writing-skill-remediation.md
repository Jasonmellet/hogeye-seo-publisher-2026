# Thread: September writing-skill remediation

- Date: 2026-09-27
- Agent: Cursor
- Status: active

## Goal

Add a fail-closed editorial gate for style, taste, flow, reader effort, and
enjoyment, then remediate the five active September V2 posts.

## Decisions

- Facts, SEO, length, and Flesch are necessary but cannot grant readiness.
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

## Open questions

- Pilot copy requires human acceptance before scaling to the remaining batch.

## Archive summary

HogEye now requires a separate editorial style/taste decision before Hub ingest
instead of treating mechanical content checks as sufficient.
