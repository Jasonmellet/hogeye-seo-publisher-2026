## Hogeye — WordPress REST + “Average Post” Analysis Plan (Read-only)

Status: **Planning / analysis only**  
Last updated: **2026-01-30**

### Goal

Before we build or push any content, we want an accurate model of how Hogeye posts are structured in WordPress:

- Gutenberg vs builder/HTML storage
- Category/tag conventions
- Featured image usage
- AIOSEO fields: whether they’re exposed via REST and how they should be set later

---

## 1) Safe REST connection confirmation (read-only)

Use the connection test in read-only mode (skips permission checks that create/delete drafts):

- `python3 test_connection.py --readonly`

This confirms:

- `WP_SITE_URL` reachable (`/wp-json`)
- authentication works (`/wp-json/wp/v2/users/me`)

Common failure mode:

- If `/wp-json/wp/v2/users/me` returns `401` with `"rest_not_logged_in"`, your infrastructure is typically **stripping the Authorization header** (common with some hosts/CDNs/security plugins). Until that’s fixed, any “create draft via REST” will fail even with valid WP application passwords.

---

## 2) “Average post shape” audit (read-only)

Run:

- `python3 scripts/seo/hogeye_wp_post_shape_audit.py --count 10`

Output:

- `work/seo/hogeye/wp_post_shape_audit.json`

What the report tells us:

- **gutenberg_blocks_share**: how often content is stored as Gutenberg blocks (`<!-- wp:... -->`)
- **top_block_types_overall**: the most common blocks (paragraph/heading/table/list/etc.)
- **featured_image_share**: how often a featured image is set
- **avg_categories_per_post / avg_tags_per_post**
- **aioseo_meta_exposed_share** + `aioseo_meta_keys_overall`: whether AIOSEO fields are accessible via REST meta

Interpretation rules:

- If `gutenberg_blocks_share` is high → we should generate Gutenberg-compatible block HTML (the pipeline already inserts `<!-- wp:image -->` blocks).
- If `aioseo_meta_exposed_share` is 0 → AIOSEO meta may not be exposed to REST; we’ll plan around either enabling REST meta exposure or using an approved alternative.

---

## 3) Smoke test: create a draft + rollback (controlled write)

Once auth works, use this script to confirm we can create a draft and cleanly roll it back:

- `python3 scripts/seo/hogeye_wp_safety_smoke_test.py`

Behavior:

- Creates 1 draft post titled `SMOKE TEST — DELETE ME — <timestamp>`
- Fetches it back with `context=edit`
- Deletes it with `force=true` (rollback)
- Writes a report: `work/seo/hogeye/wp_smoke_test_report.json`

## 4) Smoke test: AIOSEO meta update (controlled write)

Since Hogeye uses AIOSEO, we need to confirm we can set:

- meta title
- meta description
- schema settings (later, if needed)

Run:

- `python3 scripts/seo/hogeye_wp_aioseo_smoke_test.py`

Expected result:

- `aioseo_supported: true`
- fetched post includes `aioseo_head`, `aioseo_head_json`, and `aioseo_meta_data`

Report:

- `work/seo/hogeye/wp_aioseo_smoke_test_report.json`

---

## 5) Draft → review → publish workflow (plan only)

When we eventually execute, the workflow will be:

- Brief (from monthly plan + keyword universe)
- Local draft (Gutenberg-friendly structure)
- Validation checklist (internal links, schema/FAQ, meta)
- WP draft creation (one piece at a time)
- Manual review in WP
- Publish only after explicit approval

