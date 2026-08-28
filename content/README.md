# Content — WordPress JSON (canonical)

This folder is the **real on-disk location** for post and page JSON used by `scripts/publisher/publish_content_item.py` and related CLIs.

| Path | Purpose |
|------|---------|
| `posts/` | Post payloads (`*_wp_draft.json`, etc.) |
| `pages/` | Page payloads |

These files are produced by the md → JSON bridge `scripts/seo/hogeye_draft_md_to_post_json.py` from the per-cycle markdown drafts under `workspace/content_pipeline/monthly/<YYYY-MM>/drafts/`.

**Post JSON fields** (see a real file, e.g. `posts/may26_01_wp_draft.json`): `title`, `content` (HTML), `slug`, `status` (default `draft`), `excerpt`, `meta_title`, `meta_description`, `focus_keyword`, `categories` (names), `tags` (names), `faq_items` (`[{question, answer}]`). Optional: `featured_image`/`featured_image_alt`, `featured_media_id`, `date`, `enable_toc`, `content_image_count`. SEO fields map to AIOSEO via `client.config.json`.

## Relationship to `output/`

- **`output/wordpress/`** is a **symlink to this directory** — not a second copy. Use whichever path fits your mental model (`content/posts/...` in docs and examples, or `output/wordpress/posts/...` when thinking **input → output**).
- **`output/drafts/`** is different: it points at **markdown** under `workspace/content_pipeline/monthly/`. That is editorial work *before* JSON — see [`../output/README.md`](../output/README.md).

So: **one** JSON tree (`content/`), **one** draft tree (workspace monthly, visible as `output/drafts/`).
