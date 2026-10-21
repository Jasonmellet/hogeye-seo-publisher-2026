# READY FOR REVIEW: HogEye October 2026 (`2026-10`)

Hub brand: `hogeye-cameras`. Updated 2026-10-20.

Built one piece at a time through `docs/WRITING_LOOP.md`. Sentences approved by Jason on Oct 20 (`SHORTLIST.md`). The rejected Oct 16 drafts are in `_rejected_2026-10-19/` and must not be pushed.

| Row | Piece | Brief | Draft | Hub | Site |
|---|---|---|---|---|---|
| oct26_02 | Best Camera for Hog Trapping (refresh of `/hog-trapping-cameras-compared-2026-hogeye-vs-trail/`) | ready | 407 words, Gemini pass, approved by Jason | **in_review**, re-pushed Oct 20, quality **pass** | not in WP |
| oct26_01 | Trail Camera Live Feed (new) | ready | 390 words; local, Gemini, editorial pass; **waiting for Jason** | placeholder | - |
| oct26_04 | Satellite Trail Camera (new) | ready | 338 words; local, Gemini, editorial pass (style 1.29 to 1.34 vs 1.30, borderline); **waiting for Jason** | placeholder | - |
| oct26_03 | HogEye vs. Spartan GoLive (refresh) | ready | 398 words; local, Gemini, editorial pass; **waiting for Jason** | placeholder | - |
| oct26_05 | Are Hogs Nocturnal? (refresh of `/wild-hog-behavior-trap-timing/`) | ready | 393 words; local, Gemini, editorial pass; **waiting for Jason** | placeholder | - |

## oct26_02 hub flag (Oct 20)

1. "States product facts the Brand Baseline does not support (unsupported_claims p=0.90)". The draft gives the Starlink version's $2,999 price, verified on bigpigtrap.com/products.json Oct 20 and in `PRODUCT_FACTS.md`. The hub's HogEye Brand Baseline (note #9, updated Sep 26) does not mention Starlink at all. Not a wrong fact; the hub baseline is behind.
2. "Writing needs an editing pass (professional 1.18/2, confidence 0.41)". Low confidence, no specific failure. Left for Schell.

Neither reason was a wrong fact or an opening that cannot be said aloud. With Jason's OK, hub note #9 was backed up (`Wildlife Dominion Client Dashboard/.scratch/he-brand-baseline-note9-backup-2026-10-20.md`) and given the Starlink prices from `PRODUCT_FACTS.md` (Mini $2,999; Drop Trap $5,699; Panel Trap $6,895). oct26_02 was re-pushed alone and the gate returned **pass**; the gate note is gone. Row 168 kept its image; title and slug changed from "Hog Cams" / `hog-cam`, so Lily should check the image still fits.

## Gates

- [x] oct26_02 pushed alone, in_review
- [ ] Schell copy approval
- [x] Facts for oct26_01, 03, 04, 05 sourced (PRODUCT_FACTS.md) and drafted; review page `REVIEW_drafts_2-5.html`
- [ ] Jason approves #2 to #5, then push each alone (editorial gate needs `TYPESAFE_API_KEY`, from the hub `.dev.vars`)
- [ ] pull --apply after approval, then WordPress draft (refresh: needs the explicit overwrite opt-in)
