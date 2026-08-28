# Scripts

Repo-root Python is intentionally minimal: **WordPress publishing CLIs** live in **`publisher/`**, SEO tooling in **`seo/`**, Node content-system scripts at **`content-system/`**, plus **`images/`**, **`agents/`**, **`legacy/`**.

Monthly cadence (hub → pull/apply → WP draft → email): [`docs/MONTHLY_PUBLISHING_WORKFLOW.md`](../docs/MONTHLY_PUBLISHING_WORKFLOW.md).

## Dashboard (Wildlife Dominion)

```bash
npm run push:content                         # push finished posts as in_review
npm run pull:approved                        # list approved items (pipeline-ready, not live)
npm run pull:approved -- --check             # diff hub vs local (by externalId)
npm run pull:approved -- --apply --period YYYY-MM   # write hub edits → content/posts
```

`pull-approved.mjs` never publishes. After `--apply`, publish from local files — do **not** re-ingest (resets to `in_review`).

## Publisher (WordPress)

See [`publisher/README.md`](publisher/README.md). Typical commands:

```bash
./.venv/bin/python scripts/publisher/test_connection.py
./.venv/bin/python scripts/publisher/publish_content_item.py content/posts/my-post.json --type posts
```

## Other Python (images, legacy, agents)

Run from the **repository root** using module mode when the script supports it:

```bash
python -m scripts.images.analyze_images
python -m scripts.images.update_image_metadata
python -m scripts.legacy.fix_blog_block_issues
```

Legacy scripts use `_publisher_bootstrap()` so `modules.*` and `config` resolve from `scripts/publisher/`.

## Folders

- **`scripts/publisher/`**: canonical WP publish / connection-test CLIs + legacy `modules/` package
- **`scripts/seo/`**: HogEye SEO pipelines, benchmarks, DataForSEO helpers
- **`scripts/content-system/`**: Node/TS ingestion + librarian (see `package.json`)
- **`scripts/images/`**: image/media workflows
- **`scripts/agents/`**: batch image/metadata helpers
- **`scripts/legacy/`**: symlink → **`archive/legacy_wordpress_scripts/`** (older one-off fix scripts; avoid for normal monthly publishing — see `docs/DEPRECATED_SCRIPTS.md`)

