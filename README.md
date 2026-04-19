# HogEye SEO Content Publisher

WordPress publishing, HogEye SEO workflows, and content-system tooling (Python `scripts/publisher/` + Node `scripts/content-system/*`).

| Root file | Purpose |
|-----------|---------|
| `package.json`, `package-lock.json`, `tsconfig.json` | **Node/TypeScript** — `npm install` / `npm run` for `scripts/content-system/` (transcribe, librarian, `tsx`). Not used by the Python WP publisher. |
| `requirements.txt` | **Python** — core library and CLI tooling (`packages/core_py/`, `scripts/publisher/`). |
| `client.config.json` (see `client.config.example.json`) | **Publisher** — per-site WordPress and paths. |

| Start here | Purpose |
|------------|---------|
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
