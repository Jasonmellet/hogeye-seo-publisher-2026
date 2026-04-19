# HogEye Frontmatter and Provenance Rules

This system uses provenance metadata to keep ingestion auditable.

## Processed transcript required keys

- `title`
- `source_media`
- `source_filename`
- `extracted_audio` when applicable
- `transcribed_at`
- `model`
- `api`
- `language` when returned
- `duration_seconds` when returned
- `word_count`
- `raw_json`
- `raw_txt`

## Derived notes required keys

- `title`
- `source_transcript`
- `derived_at`
- `model`
- `editorial_spec_version`
- `prompt_system`
- `word_count`

## Principle

If an operator cannot tell where the artifact came from, when it was produced, and what prompt spec generated it, the artifact is incomplete.
