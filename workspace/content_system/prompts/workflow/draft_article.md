Drafting a HogEye article is a script, not a chat prompt.

Do not paste a brief into a chat and ask for a month of articles. That is how October 2026 was written in 17 minutes, and every draft was rejected.

1. The piece has a reader sentence Jason approved (`docs/WRITING_LOOP.md` phase 0) and a JSON brief that passes `scripts/seo/validate_he_briefs.py` (`docs/BRIEF_TEMPLATE.md`).
2. Run one brief:

   ```bash
   ./.venv/bin/python scripts/seo/draft_piece.py workspace/content_pipeline/monthly/YYYY-MM/briefs/<id>.json
   ```

   The writer (gpt-6-luna, reasoning effort low) gets `workspace/content_system/prompts/system/hogeye_writer_system_prompt.md` plus the reader-facing parts of the brief. The local gate (`scripts/seo/hogeye_content_quality.py`) runs, the writer fixes hard failures once, Gemini checks the draft (`scripts/seo/check_draft_second_provider.py`), and the writer fixes what Gemini names once.
3. Read the preview in `review_packets/<id>__<slug>/article.html`. Jason reads it before it goes to the hub.
4. Push that one file. Then the next brief.

To change how the writer sounds, edit the system prompt. To give it a fact, add the fact to the brief's `key_points` or to `workspace/brand_truth/PRODUCT_FACTS.md`. Never give it a rule inside a brief.
