# Content — WordPress JSON (canonical)

This folder is the **real on-disk location** for post and page JSON used by `scripts/publisher/publish_content_item.py` and related CLIs.

| Path | Purpose |
|------|---------|
| `posts/` | Post payloads (`*_wp_draft.json`, etc.) |
| `pages/` | Page payloads |
| `CONTENT_FORMAT.md` | Field notes for JSON shape |

## Relationship to `output/`

- **`output/wordpress/`** is a **symlink to this directory** — not a second copy. Use whichever path fits your mental model (`content/posts/...` in docs and examples, or `output/wordpress/posts/...` when thinking **input → output**).
- **`output/drafts/`** is different: it points at **markdown** under `workspace/content_pipeline/monthly/`. That is editorial work *before* JSON — see [`../output/README.md`](../output/README.md).

So: **one** JSON tree (`content/`), **one** draft tree (workspace monthly, visible as `output/drafts/`).
