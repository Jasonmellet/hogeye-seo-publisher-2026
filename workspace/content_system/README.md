# HogEye Content System

This folder holds the Theo-style doctrine and workflow layer that now sits underneath the existing HogEye monthly content pipeline.

## Purpose

- continuously ingest source material
- turn transcripts into reusable derived notes
- keep prompts anchored to HogEye truth files
- validate artifacts before approval handoff

## Start here

- `config/evidence_and_truth.md`
- `config/artifact_contract.md`
- `workflows/ingestion_workflow.md`
- `workflows/editorial_workflow.md`
- `workflows/phase_two_wordpress_bridge.md`
- `workflows/librarian_workflow.md`

## Librarian commands

```bash
npm run librarian:audit -- --limit 10
npm run librarian:apply -- --proposal /abs/path/to/proposal.json
```
