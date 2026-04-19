# Repo layout (single client: HogEye)

## Local-first mental model: input → output

| | Path |
|---|------|
| **Stuff you add** (media, transcripts, notes) | **`input/`** (see `input/README.md`) |
| **Final drafts** (markdown before WP JSON) | **`output/drafts/<YYYY-MM>/drafts/`** (symlink → `workspace/content_pipeline/monthly/`) — `<YYYY-MM>` = **target publication month**, see `workspace/content_pipeline/monthly/README.md` |
| **What you push to WordPress** (JSON + `publish_content_item.py`) | **`content/posts/`** (and `content/pages/`) — canonical on disk |

**`output/wordpress/` is the same directory as `content/`** (symlink). There is no second JSON tree — only two names for one folder. Use `content/…` in commands and docs, or `output/wordpress/…` when you want everything under “output” next to `input/`.

`input/` and `output/` are **symlinks** so you do not have to remember long paths under `workspace/`. See [`content/README.md`](../content/README.md) and [`output/README.md`](../output/README.md).

## Legacy / other folders (when you need them)

| Folder | Role |
|--------|------|
| `workspace/` | Full program: pipeline, SEO strategy, `PROJECT_CONFIG.json`, librarian, monthly folders (same markdown as `output/drafts/` + sources). |
| `content/` | **Canonical** WordPress JSON (`posts/`, `pages/`). `output/wordpress/` is a symlink here — not a duplicate. |
| `seo/plan/` | Keyword CSVs you keep in the repo. |
| `work/` | Local scratch from benchmarks / big exports (optional). |

## Engines (mental model)

1. **Editorial** — write under `output/drafts/**` (final markdown per article).
2. **Convert** — `hogeye_draft_md_to_post_json.py` → `content/posts/*.json` (same path as `output/wordpress/posts/`).
3. **Publish** — `scripts/publisher/publish_content_item.py content/posts/your.json` (or `output/wordpress/posts/your.json`).
