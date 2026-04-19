# Input — put new data here

Everything you **add** to the system should land under one of these folders (same paths the pipeline uses under `workspace/`).

| Folder | Purpose |
|--------|---------|
| `media_inbox/` | Video/audio to transcribe (then run `npm run transcribe`). |
| `transcripts_raw/` | Whisper JSON + `.txt` sidecars from transcription. |
| `source_notes/` | Free-form notes / intake. |
| `derived_notes/` | Structured notes extracted from transcripts. |
| `raw_content/` | Legacy bulk import (Word/PDF → JSON). |

These are **symlinks** into `workspace/content_pipeline/sources/` (except `raw_content` → repo `raw_content/`). Edit files anywhere; you do not need to remember the long path.
