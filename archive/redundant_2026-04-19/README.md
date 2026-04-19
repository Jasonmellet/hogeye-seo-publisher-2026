# Retired redundant paths (2026-04-19)

Housekeeping after moving the HogEye workspace to repo-root `hogeye/` and deduplicating tooling.

| Folder | What | Action |
|--------|------|--------|
| `seo_root_duplicate_scripts/` | Byte-identical copies of `scripts/seo/*.py` that also lived under `seo/` | Removed from `seo/`; use **`scripts/seo/`** only. |
| `stale_smoke_tests_from_seo_root/` | Older `seo/` copies of `hogeye_wp_*_smoke_test.py` missing `WP_ALLOW_DELETE` / `wp_delete_guard` safety | **Canonical:** `scripts/seo/hogeye_wp_aioseo_smoke_test.py` and `scripts/seo/hogeye_wp_safety_smoke_test.py`. |
| `seo_hogeye_macos_duplicate_md/` | macOS “duplicate” files (`* 2.md`) in `seo/hogeye/` | Kept the originals without the ` 2` suffix. |
| *(removed)* | `.claude/worktrees` snapshot (~4MB) | **Deleted** (not stored in git). `.claude/` is gitignored so it does not reappear in commits. |

Also removed **duplicate markdown at repo root** that matched `docs/` byte-for-byte (`QUICK_START.md`, `NEW_CLIENT_CHECKLIST.md`, `GOOGLE_CLOUD_API_ENABLEMENT.md`, `DATAFORSEO_BIBLE.md`). Canonical copies: **`docs/*.md`**.

Three scripts that previously existed **only** under `seo/` were moved into **`scripts/seo/`** (not retired): `hogeye_competitor_keyword_gap.py`, `hogeye_paa_extractor.py`, `hogeye_seo_monitor_check.py`.

This tree was moved from `retired/redundant_2026-04-19/` into **`archive/`** in 2026-04; delete only when you are sure nothing is needed for forensics.

---

**2026-04-19 (later):** Removed **26** root-level `.md` files that were byte-identical to `docs/` (canonical copy is always `docs/`). Root now keeps only: `README.md`, `DOCS.md`, `starter.md`, `CLIENT_SETUP.md`, `AGENT_LIBRARIAN.md`, `AGENT_SEO_MONITOR.md`. Moved `startup.md` → `docs/STARTUP.md` and `WORDPRESS_PUBLISHING_REPLICATION_GUIDE.md` → `docs/`.

**2026-04-19 (later still):** Moved operator + agent docs off the repo root: `starter.md` → `docs/starter.md`, `DOCS.md` → `docs/INDEX.md`, `CLIENT_SETUP.md` → `docs/CLIENT_SETUP.md`, `AGENT_*.md` → `docs/agents/`. Root keeps only **`README.md`** as the landing pointer.
