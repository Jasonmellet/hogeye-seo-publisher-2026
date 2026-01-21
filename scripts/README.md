# Scripts

This folder holds **non-module** scripts grouped by purpose so the repo root stays clean.

## How to run

Run from the repo root using Python module mode:

```bash
python -m scripts.images.analyze_images
python -m scripts.images.update_image_metadata
python -m scripts.legacy.fix_blog_block_issues
```

This ensures imports like `config` and `modules.*` resolve correctly.

## Folders

- **`scripts/images/`**: image/media workflows (metadata batching, featured image helpers)
- **`scripts/agents/`**: agent batching + progress scripts for media metadata work
- **`scripts/legacy/`**: older one-off fix scripts (kept for reference; avoid for monthly publishing)

