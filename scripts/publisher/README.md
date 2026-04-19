# WordPress publisher (Python)

Run these from the **repository root** (paths assume `content/` or **`output/wordpress/`** (same files), `.env`, and `client.config.json` at the root).

| Script | Use |
|--------|-----|
| `test_connection.py` | Verify WP REST auth and site guardrails before publishing. |
| `publish_content_item.py` | Publish **one** JSON under `output/wordpress/posts/` or `…/pages/` (same as `content/posts` / `content/pages`). |
| `publish_batch.py` | Publish **many** JSON files. |
| `resolve_internal_links.py` | Resolve `{{link:…}}` across the site (prefer `--dry-run` first). |
| `update_landing_page.py` | Thin wrapper around the pipeline for a single page JSON. |
| `publish_draft_page.py` | Flip an existing WP **page** draft to published (by ID). |
| `audit_site.py` | Read-only inventory via REST (legacy stack). |

Legacy compatibility modules live in **`modules/`** next to these scripts (`from modules.auth import …`).

Path bootstrap: each entry script calls `_publisher_bootstrap()` so `modules`, `config`, and `agt_publisher_core` resolve without extra `PYTHONPATH`.
