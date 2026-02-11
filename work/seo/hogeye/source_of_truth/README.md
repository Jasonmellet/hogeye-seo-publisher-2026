# Hogeye source of truth (local)

This folder is meant to hold **the authoritative snapshot(s)** of what already exists on the Hogeye website, so we can:

- avoid publishing duplicate/cannibalizing content
- fact-check new drafts against existing pages/posts
- verify modifications to existing content (refresh snapshot and diff)

## WordPress metadata snapshot (recommended)

Exports **metadata + all copy** for all posts + pages into:

- `work/seo/hogeye/source_of_truth/wp/`

Run:

```bash
python3 scripts/seo/hogeye_wp_clone_metadata.py --project-root "$(pwd)" --include-copy --include-copy-hashes
```

Outputs:

- `wp/snapshot_manifest.json`: run metadata + counts
- `wp/posts_metadata.jsonl`: one JSON object per post
- `wp/pages_metadata.jsonl`: one JSON object per page
- `wp/taxonomies.json`: categories/tags maps (optional)

Copy format:

- Copy is exported as **plain text** (HTML stripped) under `copy.content_text` and `copy.excerpt_text`
- Hashes are exported under `copy_hashes.*` to make “duplicate copy” checks fast

## Refresh workflow

- After publishing or updating content in WordPress, re-run the exporter.
- Use git (or your diff tool) to compare `wp/*` between snapshots/commits.
