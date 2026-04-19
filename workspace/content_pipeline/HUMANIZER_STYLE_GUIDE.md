# HogEye Humanizer Style Guide (Fact-Locked)

Use this guide after first draft and before QA.

Goal: make copy read like a strong field operator + skilled copywriter, without changing facts.

**This file is the canonical punctuation + voice pass for HogEye drafts.** The Librarian workflow assumes you have applied it (see `docs/agents/AGENT_LIBRARIAN.md`). The SEO Monitor Gate can treat violations here as **FAIL** (see `docs/agents/AGENT_SEO_MONITOR.md`).

## Punctuation (non-negotiable)

**No em dashes. Ever.** Do not use the em dash character (U+2014, `—`) in titles, meta, body, FAQs, or CTAs.

Use normal, human punctuation instead:

- **Commas** for short asides or lists.
- **Periods** to split overloaded sentences.
- **Colons** to introduce an explanation.
- **Parentheses** for true asides.
- **"and" / "or"** where two clauses belong in one sentence.

**Numeric ranges:** Use ASCII hyphen with no spaces (`2-3 nights`, `7-14 days`, `$150-$400`). Do not use en dash (U+2013) in new copy unless your toolchain already normalizes it.

**Before you mark humanization done:** Search the draft for `—` (em dash). If you find any, replace and re-read.

## Core rule

Humanize wording, not truth.

- Do: improve flow, rhythm, clarity, and emphasis.
- Do not: add new claims, numbers, use cases, or outcomes.

## Target voice profile

- Practical and direct
- Field-aware and process-oriented
- Confident but not hype-heavy
- Helpful and specific
- Clean, plain-English sentences

Think: "TJ explaining setup and decision quality to a serious operator."

## Allowed edits

- shorten awkward sentences
- replace generic phrases with concrete action language
- improve transitions between sections
- tighten repetitive wording
- add clear lead-in lines before checklists
- convert stiff phrasing into natural, professional wording
- replace em dashes with commas, periods, or colons (required, not optional)

## Disallowed edits

- adding facts not present in research pack
- adding statistics/percentages not sourced
- adding testimonials or case stories not sourced
- adding broad positioning (security/surveillance/property monitoring)
- using banned audience term `ranchers`
- introducing em dashes (`—`) or decorative punctuation that reads like AI filler

## Style moves to prefer

- Use action verbs: monitor, verify, trigger, confirm, validate, tighten, check.
- Use short "why this matters" lines after key steps.
- Use concise section openers that answer intent quickly.
- Keep FAQ answers direct (2-5 sentences).

## Tone guardrails

- Avoid fluff: "game changer", "revolutionary", "ultimate", "best ever".
- Avoid fake urgency and inflated certainty.
- Keep confidence tied to process quality, not guaranteed outcomes.

## Fact-lock check (required)

After humanizing, confirm:

1. Every claim still maps to source-backed evidence.
2. No new performance claim was introduced.
3. No banned framing or banned words were introduced.
4. Positioning remains wild hog trap monitor focused.
5. **No em dash (`—`) remains in the file.**

If any fail, revert those edits before QA.
