# Monthly Publishing Workflow (10 items/month)

This repo is now designed so you can publish a single piece of content and have it be **~90% correct on the first run**.

The rule: **use the canonical pipeline** and avoid running old one-off “fix scripts.”

---

## Canonical commands

Before you publish, ensure:
- You created `client.config.json` (from `client.config.example.json`) and it matches your target site
- You ran `python3 test_connection.py`

### Publish one item (recommended)

- **Blog post**

`python3 publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts`

- **Landing page**

`python3 publish_content_item.py /absolute/path/to/content/pages/my-page.json --type pages`

By default this publishes/updates as **draft** and runs **validation gates** (FAQ count, image rules, placeholders, etc.).

### Publish a batch (directory or list of files)

- **Posts**

`python3 publish_batch.py /absolute/path/to/content/posts --type posts`

- **Pages**

`python3 publish_batch.py /absolute/path/to/content/pages --type pages`

---

## What the pipeline enforces automatically

### Blog posts

- Consistent spacing (P/H2/H3/LI)
- Fixes common Gutenberg breakage patterns (malformed H2 styles)
- Optional TOC (auto on long posts, or `--enable-toc`)
- Featured image auto-selection (if not provided)
- Adds in-body images at natural break points (keeps it in the 2–4 range by default)
- Featured image should **not** appear in the body
- Optional FAQ validation: you can enforce an exact count via `--faq-questions N` (default is **no enforcement**)

### Landing pages

- Consistent spacing
- Converts to **ACF interior blocks** only when it is safe to do so:
  - Explicitly enabled in the source JSON (`use_acf_blocks: true`), OR
  - The existing WP page is already using the interior template (`template-interior.php`)
- Validates the page has H2 structure (basic structural gate)
- Optional **protected marker** safety (configured per-client in `client.config.json` via `protectedMarkersBySlug`)

---

## Safety notes
- If you run with `--status publish`, you will be asked to confirm the client name unless you pass `--yes` (automation).
- If `DRY_RUN=true`, the pipeline **does not write to WordPress** (it validates locally and exits successfully when gates pass).

---

## What you do manually (fast checklist)

- Preview in WP admin (desktop + mobile)
- Confirm images “feel right” (topic fit)
- Confirm final internal links once the full set of pages/posts is stable

---

## What to avoid

- Don’t run random `fix_*` scripts unless you’re intentionally repairing legacy content.
- Don’t “patch” live WordPress content manually and then rerun automation (it creates drift).

If you need a repair, use the canonical pipeline + adjust the source JSON, then re-run.

**Legacy scripts** are now stored under `scripts/legacy/` (see `DEPRECATED_SCRIPTS.md`).
