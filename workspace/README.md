# Client workspace (repo root)

This folder is the **canonical working tree** for HogEye content operations: monthly pipeline (`content_pipeline/`), ingestion, `content_system/`, strategy and registry docs (for example `CONTENT_REGISTRY.md`, `HOGEYE_CONTENT_STYLE_GUIDE.md`), `PROJECT_CONFIG.json`, exports, and ops. Former duplicate paths under `seo/hogeye/` were merged here so there is a single tree.

Historical baselines, retired duplicate tooling, and stale legacy script copies live under **`archive/`** (see `archive/README.md`) — not here.

**Monthly folder names (`2026-04`, `2026-05`, …) mean target *publication* month**, not “the month we researched keywords.” See **`content_pipeline/monthly/README.md`**.

**Final drafts for review** live under `content_pipeline/monthly/<YYYY-MM>/drafts/` as `<article_id>_draft.md`. QA checklists are sibling `qa/`; WordPress-ready JSON is generated into `content/posts/` at the repo root.

If you relocate this directory, set **`WORKSPACE_REL`** (preferred) or **`HOGEYE_WORKSPACE_REL`** in `.env` to the new repo-relative path (default: `workspace`).

**WordPress publisher CLIs** live under **`scripts/publisher/`**. **SEO / benchmark scripts** are under **`scripts/seo/`**.
