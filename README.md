# HogEye SEO Content Publisher

WordPress publishing, HogEye SEO workflows, and content-system tooling (Python `scripts/publisher/` + Node `scripts/content-system/*`).

**Shared SEO / monthly / CMS-draft specs (all AGT repos):** [AGT Docs Hub](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/overview). This repo keeps HogEye doctrine and WordPress gates.

| Root file | Purpose |
|-----------|---------|
| `package.json`, `package-lock.json`, `tsconfig.json` | **Node/TypeScript** — `npm install` / `npm run` for `scripts/content-system/` (transcribe, librarian, `tsx`). Not used by the Python WP publisher. |
| `requirements.txt` | **Python** — core library and CLI tooling (`packages/core_py/`, `scripts/publisher/`). |
| `client.config.json` (see `client.config.example.json`) | **Publisher** — per-site WordPress and paths. |

| Start here | Purpose |
|------------|---------|
| [AGT Docs Hub](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/overview) | Shared SEO / monthly / draft-first CMS specs (Confluence) |
| [`docs/MONTHLY_PUBLISHING_WORKFLOW.md`](docs/MONTHLY_PUBLISHING_WORKFLOW.md) | **HogEye monthly cycle** (hub status → pull/apply → WP draft → team email) |
| [`.cursor/skills/he-monthly-cycle/SKILL.md`](.cursor/skills/he-monthly-cycle/SKILL.md) | Agent skill for that cycle (WordPress, not Shopify) |
| [`docs/starter.md`](docs/starter.md) | Operator + agent setup, HogEye paths, safety rules |
| [`docs/INDEX.md`](docs/INDEX.md) | Full documentation map |
| [`docs/REPO_LAYOUT.md`](docs/REPO_LAYOUT.md) | **Input vs output** (`input/`, `output/`) + legacy folder names |
| [`input/README.md`](input/README.md) | Where to drop media, transcripts, notes |
| [`output/README.md`](output/README.md) | Symlink shortcuts: drafts + `wordpress/` (same files as `content/`) |
| [`content/README.md`](content/README.md) | Canonical WordPress JSON (`posts/`, `pages/`) — `output/wordpress/` points here |
| [`docs/agents/`](docs/agents/) | Cursor agent personas (Librarian, SEO Monitor, …) |
| [`workspace/README.md`](workspace/README.md) | HogEye workspace: monthly pipeline, drafts, `PROJECT_CONFIG.json` |
| [`archive/README.md`](archive/README.md) | Superseded or duplicate material (pre-North Star snapshots, retired script copies, stale legacy duplicate) — **not** current workflow |

Entry points: `scripts/publisher/publish_content_item.py`, `scripts/publisher/test_connection.py`. Technical detail: [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md).

### Dashboard-approved content (publish pipeline gate)

**Approved** in the Wildlife Dominion dashboard means content is ready for the publish pipeline — it is **not** live on WordPress/Shopify yet. Live publish still requires `--approved-in-dashboard` (or the interactive `APPROVED` prompt).

For approved posts, **the hub is source of truth until publish** (Schell/reviewer edits live in hub `bodyMd`). Sync those edits into local `content/posts/*.json` before publishing; then publish from the local files. **Do not re-ingest** after `--apply` — a re-push to `/api/ingest` resets status to `in_review`.

```bash
# Requires DASHBOARD_URL + WD_INGEST_KEY in gitignored .env (see .env.example)
npm run pull:approved
npm run pull:approved -- --period 2026-07 --json
npm run pull:approved -- --fail-if-none --out approved.json

# Diff hub vs local (exit 1 if drift). Match by externalId, not slug.
npm run pull:approved -- --check --period 2026-07

# Write hub title/slug/bodyMd(/focus_keyword) → local JSON, then publish from local files
npm run pull:approved -- --apply --period 2026-07
```
