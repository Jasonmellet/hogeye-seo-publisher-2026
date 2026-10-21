# Thread: HogEye writing-process fix and October 2026 rebuild

- Date: 2026-10-20
- Agent: Claude Code
- Status: active

## Goal

Port the Boar Blanket writing-process fix (Boar Blanket PR #9) to HogEye, then rebuild October 2026 one piece at a time. October had been drafted in 17 minutes from prompts made of prohibitions, and the drafts recited those rules back to the reader.

## Decisions

- Every October piece starts from a reader sentence Jason approves and real search evidence. Filling a paid slot is not a reason to write.
- Length is a range (450 to 750 words), not an 800 ±5% band.
- The writer sees only reader-facing facts. The writer is gpt-6-luna at low effort; Gemini is the second-provider checker, because there is no xAI key.
- The TL;DR is optional, following the canonical WRITING_LOOP.md. The September rule now applies only when a TL;DR is present (35 to 60 words).
- "trail camera" is allowed as a search phrase, but HogEye is never called one. "Steel" is retired as a product name.
- Prices must appear in `workspace/brand_truth/PRODUCT_FACTS.md`, which comes from bigpigtrap.com/products.json (Oct 20, 2026).
- HogEye's October stays off Boar Blanket's topics (bait, feeders) and Big Pig's (cellular hog trap, doors and gates, triggers, trap buying guides).

## Changes

- `scripts/seo/validate_he_briefs.py`: new brief contract. Checks `reader_sentence`, `sentence_approved`, `evidence`, and `facts_pending`, and fails slot filler and writer rules written as key points.
- `scripts/seo/hogeye_content_quality.py`: removes the band. Adds checks for rules written as prose, repeats, em dashes, the "Steel" name, and prices.
- `scripts/seo/he_writer.py`, `draft_piece.py`, `check_draft_second_provider.py`: one-piece writer and Gemini check.
- `workspace/content_system/prompts/system/hogeye_writer_system_prompt.md`: rewritten as the model's actual prompt.
- `scripts/push-content.mjs`: from 2026-10, one file per push, which needs a passing check and a valid brief.
- `workspace/content_pipeline/monthly/2026-10/`:
  - `SHORTLIST.md` and the briefs
  - `_rejected_2026-10-19/`, holding the old drafts out of the push path
- `docs/WRITING_LOOP.md`: now matches the canonical root copy. `docs/BRIEF_TEMPLATE.md` is new.

## Verification

- `./.venv/bin/python -m pytest -q tests`: 38 pass. The five rejected October drafts fail the gate.
- `npm run typecheck`: pass.
- Hub row `oct26_02`, re-pushed alone on Oct 20: `quality=pass`, `in_review`, image attached.

## Open questions

- Facts still needed before the other October briefs can be drafted:
  - `oct26_01`: HogEye's signal guidance
  - `oct26_03`: Spartan GoLive facts
  - `oct26_04`: what the Starlink version includes and what it costs
  - `oct26_05`: an extension source on hog feeding times
- `editorial-gate.mjs` needs `TYPESAFE_API_KEY`, which is not in `.env`.
- The root WRITING_LOOP.md still says HogEye keeps its own writer until a sample is chosen.

## Archive summary

HogEye now drafts one approved piece at a time through a brief contract, a writer prompt that holds no rules for the copy, gates that police leaks and repeats rather than keyword placement, and a Gemini check before Jason reads anything. The October drafts from Oct 16 were rejected and moved out of the push path. `oct26_02` (best camera for hog trapping) is in the hub for Schell, and the other four pieces are waiting on facts.
