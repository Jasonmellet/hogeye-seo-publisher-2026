# Publish Safety Mandate (HogEye / Wildlife Dominion)

**Shared spec (canonical):** [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684/Draft-first+CMS+publishing) on the AGT Docs Hub. Improve that page from any publisher repo. Do not fork Approved-≠-live / create-only / no-auto-images / meta-required rules into a competing local playbook.

This file keeps **HogEye WordPress command detail** only (paths, env, AIOSEO field names for this stack).

## HogEye sequence (local)

A. `node scripts/pull-approved.mjs --period=YYYY-MM`  
B. `node scripts/pull-approved.mjs --check --period=YYYY-MM`  
C. `node scripts/pull-approved.mjs --apply --period=YYYY-MM` (then `--check` must be clean)  
D. Ensure each local publish JSON has: title, slug, content/html, meta_title, meta_description, focus_keyword, categories / wp_category_id.  
E. If slug exists on WP (post **or** page, any status): do **not** update — create a fresh draft under a unique slug (e.g. `…-YYYY-MM-refresh`) unless `--allow-update-existing` or JSON `update_existing: true` was ordered. Stored `wp_post_id` alone is not opt-in.  
F. Publish as `--status draft` only. No auto-images. No `--resolve-links` unless needed and stable.  
G. Verify every draft: status=draft, categories set, SEO title/description/keyphrase set (hard-fail if missing), featured_media=0, zero auto-inserted body images, correct author.  
H. Report: slug, wp_id, edit URL, category, meta title, focus kw, notes.

## HogEye preflight

Before any WP writes: confirm `.env` has `WP_*` + `DASHBOARD_URL` + `WD_INGEST_KEY` + `WD_BRAND=hogeye-cameras`, `client.config.json` matches hogeyecameras.com, and `./.venv/bin/python scripts/publisher/test_connection.py` succeeds.

## Hard fails (stop and ask)

Follow the Confluence non-negotiables. Local stop conditions also include: WP credentials missing / wrong site; urge to “just update by slug” for convenience.
