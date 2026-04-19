# Archive — not active source of truth

Material here is **historical, superseded, or duplicate**. Do not treat these paths as inputs for current HogEye publishing or strategy unless you are deliberately recovering old state.

| Path | Contents |
|------|----------|
| `redundant_2026-04-19/` | Duplicate `seo/` scripts, stale smoke-test copies, macOS `* 2.md` duplicates — kept after consolidating on `scripts/seo/` and `workspace/`. See `redundant_2026-04-19/README.md`. |
| `workspace_pre_northstar/` | Pre–North Star baselines: live WP draft JSON backups, git snapshot of planning docs at `457fd1c`. See `workspace_pre_northstar/README.md`. |
| `legacy_wordpress_scripts/` | One-off WordPress HTML patch scripts (camp/FAQ/TOC era). **Canonical on disk** for this code; `scripts/legacy` at repo root is a **symlink** here so `python -m scripts.legacy.<module>` still works. Documented in `docs/DEPRECATED_SCRIPTS.md`. |
| `legacy_root_stale_duplicate/` | Older duplicate of the same legacy scripts that lived at repo-root `legacy/` (a few files lagged `scripts/legacy/` on safety/config). **Do not run** — use `legacy_wordpress_scripts/` only. |
| `agents_root_duplicate_scripts_agents/` | Byte-identical copy of what lives under **`scripts/agents/`** (was an extra top-level `agents/`). |
| `images_root_duplicate_scripts_images/` | Byte-identical copy of what lives under **`scripts/images/`** (was an extra top-level `images/`). |

New archival drops should get a dated subfolder under `archive/` and a one-line entry in this table.
