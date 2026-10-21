# HogEye brief, October 2026 on

A brief tells the writer what the reader should do. Everything in it except `evidence`, `sentence_approved`, and `notes` is sent to the writing model, so every field the writer sees must be something a reader could see.

`scripts/seo/validate_he_briefs.py` enforces this for any brief with `period` 2026-10 or later. `scripts/seo/draft_piece.py` refuses a brief that fails it, and `scripts/push-content.mjs` refuses a post whose brief fails it.

Briefs live in `workspace/content_pipeline/monthly/YYYY-MM/briefs/<external_id>.json`.

## Order

1. Research picks the candidates. Each one needs a search signal from GSC, GA4, DataForSEO, Semrush, or a client request. Losing pages are refresh candidates, and a refresh counts as one piece.
2. Write one reader sentence per candidate in `SHORTLIST.md` (WRITING_LOOP.md phase 0). Jason approves the list before any drafting.
3. If there are fewer real candidates than paid slots, say so and wait. Filling a slot is not a reason to write.
4. Reuse the month's hub row by `external_id`, so Lily's image stays attached. Never use the slug as the id.
5. Draft one piece at a time with `draft_piece.py`, read it, and push that piece only.

## Shape

Example values only; the evidence numbers here are not real.

```json
{
  "brief_id": "oct26_05",
  "external_id": "oct26_05",
  "period": "2026-10",
  "type": "new",
  "title": "How to Count Hogs on Camera Before You Close the Trap",
  "slug": "count-hogs-on-trail-camera",
  "target_keyword": "count hogs on trail camera",

  "reader_sentence": "Watch your trap for three or four nights and count every hog that shows up, inside and outside, and only send the close command once that whole number is inside.",
  "sentence_approved": { "by": "Jason", "on": "2026-10-21" },
  "evidence": [
    { "source": "gsc", "signal": "count hogs on camera queries: 120 impressions/90d, position 18" }
  ],

  "word_count": 750,
  "min_words": 450,
  "key_points": [
    "The HogEye Mini Camera streams live video to the HogEye app, day or night.",
    "Hogs that escape a partial catch learn to avoid the trap."
  ],
  "h2_outline": ["Count for several nights", "Inside versus outside", "When the number matches"],
  "internal_links": [
    { "anchor": "hog trap camera", "url": "https://hogeyecameras.com/steel-camera/" }
  ],
  "faq_questions": [],
  "categories": ["Feral Hog Monitoring"],
  "tags": ["sounder", "trap timing"]
}
```

## Fields

| Field | Seen by writer | Rule |
| --- | --- | --- |
| `reader_sentence` | yes | One sentence a landowner could say on the phone. It names the situation and the move. Not the keyword with grammar around it. |
| `sentence_approved` | no | Who approved the sentence and when. No draft without it. |
| `evidence` | no | At least one `{source, signal}`. `source` is gsc, ga4, dataforseo, semrush, or client. |
| `word_count` | yes | The length ceiling. Over 110% fails. |
| `min_words` | yes | Optional floor. Under it gets one writer fix pass, then only a warning. October 2026 is 450 to 750. |
| `key_points` | yes | Facts the reader can use, as plain sentences. Never rules for the writer such as "Do not claim the camera closes the gate" or "No surveillance framing". Those get written into the article. The validator fails a key point that reads as a rule. |
| `internal_links` | yes | Only pages the reader needs next. There is no minimum. |
| `h2_outline` | yes | Optional suggestions. The writer may merge or drop them. |
| `faq_questions` | yes | Optional. Leave empty unless people ask questions the body would not answer. |
| `type`, `existing_url` | yes | `update` means a refresh of `existing_url`. The WordPress step still needs an explicit overwrite opt-in. |
| `categories`, `tags` | no | Live WordPress taxonomy. |
| `notes` | no | Anything for Jason or the next session. Never "fills the paid count". |

Rules for the writer belong in `workspace/content_system/prompts/system/hogeye_writer_system_prompt.md`, product facts and prices in `workspace/brand_truth/PRODUCT_FACTS.md`, and policing in `scripts/seo/hogeye_content_quality.py` or the checker. They do not go in the brief.
