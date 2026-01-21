# Workspace Artifacts (`work/`)

This repo generates a lot of **run artifacts** (image lists, batch outputs, agent tracking files).  
To keep the repo root clean and “monthly-ready”, we store all non-source artifacts under `work/`.

`work/` is **git-ignored**.

## Layout

- **`work/image-metadata/inputs/`**
  - Input lists like `image_remaining_unprocessed*.{csv,json}`, `priority_images.json`, `images_to_process.json`
- **`work/image-metadata/outputs/`**
  - Generated metadata, progress, and batch results (e.g. `priority_images_metadata.json`, `processing_status.json`)
- **`work/image-metadata/batches/`**
  - Per-batch download manifests (e.g. `image_batch_1_for_analysis.json`)
- **`work/image-metadata/temp_images_for_analysis/`**
  - Downloaded images for manual review
- **`work/agents/`**
  - Agent tracking + questions (e.g. `agent2_done_ids.txt`, `agent3_questions.txt`)

## Common commands

- **Image batch download**:

```bash
python -m scripts.images.analyze_images
```

- **Update WordPress image metadata**:

```bash
DRY_RUN=true python -m scripts.images.update_image_metadata
python -m scripts.images.update_image_metadata
```

## Notes

- Canonical monthly publishing scripts remain in the repo root (see `MONTHLY_PUBLISHING_WORKFLOW.md`).
- Agent/image scripts prefer `work/` paths but include legacy fallbacks when possible.

