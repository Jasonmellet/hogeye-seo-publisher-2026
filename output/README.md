# Output — operator shortcuts (not duplicate data)

`output/` is **two symlinks**, not a separate content store:

| Symlink | Target | What you put there |
|---------|--------|---------------------|
| `drafts/` | `workspace/content_pipeline/monthly/` | **Markdown** drafts: `YYYY-MM/drafts/<article_id>_draft.md` |
| `wordpress/` | `content/` | **WordPress JSON**: `posts/*.json`, `pages/*.json` |

So **`output/wordpress/` and `content/` are the same folder** (same files on disk). Docs and scripts often say `content/posts/…` because that is the canonical path; `output/wordpress/` exists so “everything you ship” can live under `output/` next to `input/`.

**Not the same as drafts:** markdown lives under `drafts/` (the monthly pipeline). JSON lives under `content/` (alias: `output/wordpress/`).

## Operator workflow

1. **Final draft** — edit `drafts/…/<article_id>_draft.md` (or the same path under `workspace/content_pipeline/monthly/`). Copy to Google Docs if you use external approval.
2. **Convert** — `hogeye_draft_md_to_post_json.py` → write JSON under `content/posts/` (or `output/wordpress/posts/` — same thing).
3. **Publish** — `publish_content_item.py` with that JSON path.

**Mechanical flow:** `drafts/…/<article_id>_draft.md` → `hogeye_draft_md_to_post_json.py` → `content/posts/*.json` → `publish_content_item.py`. (Legacy alias: `hogeye_humanized_md_to_post_json.py`.)

`handoff/` under each month is optional scaffolding, not part of this flow unless you want it.

More detail on the JSON tree: [`../content/README.md`](../content/README.md).
