# HogEye Ingestion Workflow

## Accepted inputs

- video files dropped into `workspace/content_pipeline/sources/media_inbox/`
- article or website-copy files ingested through `npm run ingest-source -- <path>`
- existing website snapshots already stored in `workspace/source_of_truth/`

## Video path

1. Drop media into `sources/media_inbox/` or pass an absolute path directly.
2. Run `npm run transcribe -- --auto <media-path>`.
3. Review:
   - `sources/transcripts/raw/`
   - `sources/transcripts/processed/`
   - `sources/derived_notes/`

## Text/article path

1. Save a local text, markdown, or html file.
2. Run `npm run ingest-source -- <file-path>`.
3. Use the created source note in briefs or research packs.

## Operating rule

Media is transient. Text artifacts and provenance are durable.
