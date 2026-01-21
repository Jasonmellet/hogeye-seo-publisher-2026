# Camp Lakota WordPress Publishing Deep Dive (Landing Pages + Blog Posts)

**Last updated:** 2026-01-13  
**Scope:** Lessons learned publishing/updating landing pages and blog posts on the Camp Lakota WordPress instance using the REST API + Python automation.

This document is a **comprehensive “what went wrong / what worked / how to avoid repeating mistakes”** reference. It complements (doesn’t replace):
- `PROJECT_STATUS.md` (progress/status + known issues)
- `PAGE_ENHANCEMENT_GUIDELINES.md` (gold-standard layout rules)
- `MIGRATION_PLAN.md` (URL migration + redirect strategy)
- `LANDING_PAGE_DESIGN_TEMPLATE.md` and `BLOG_POST_DESIGN_TEMPLATE.md` (design patterns)

---

## Why this project was harder than “just upload HTML”

WordPress is not a static HTML bucket. In this instance, the biggest complexity was:
- **Block editor (Gutenberg) storage**: content is stored as a structured stream of blocks (HTML + block comments), and the editor validates it.
- **Custom ACF blocks**: several high-quality “reference” pages (e.g., “Our Story”) are built using **custom ACF blocks**, not raw HTML.
- **Theme/template coupling**: layout/spacing/hero behavior is partially controlled by the theme template and block markup, not only the HTML we send.
- **REST API constraints**: some fields are easy to update (`content`, `featured_media`), others require `context=edit`, and SEO meta verification is limited.
- **Operational risk**: many landing pages already existed and were live; updating the wrong object or running scripts twice could degrade live content.

---

## Core realities of this WordPress instance (what we discovered)

### ACF blocks vs raw HTML (the “Our Story” revelation)
- **What happened**: We tried to “match” the Our Story look by inserting well-styled raw HTML.
- **Why it didn’t match**: Our Story uses **custom ACF Gutenberg blocks**, which the theme styles consistently.
- **How we fixed it**: We extracted the Our Story block structure (`our_story_page_structure.json`, `our_story_full_content.txt`) and built converters:
  - `convert_to_acf_blocks.py` (single page)
  - `convert_all_landing_pages_to_acf.py` (apply across pages)
- **Advice**:
  - **DO** treat the best-looking reference page as the “source of truth” for block structure.
  - **DON’T** assume raw HTML will render identically if the theme expects ACF blocks.

### Gutenberg block validation (“Block contains unexpected or invalid content”)
- **What happened**: small malformed HTML (notably bad `style="..."` attributes on headings) caused block validation errors in the WP editor.
- **How we fixed it**: `fix_blog_block_issues.py` normalized malformed H2 styles across posts.
- **Advice**:
  - **DO** keep transformations minimal and deterministic.
  - **DO** run a “block sanity check” pass after any regex-based edits.
  - **DON’T** do string replacements that can produce invalid nested/duplicate attributes.

### REST API response noise (PHP warnings)
- **What happened**: WordPress sometimes returned PHP warnings in API responses, which can break `json.loads` and downstream automation.
- **How we overcame it**: scripts were hardened to tolerate/clean noisy responses, and we relied on HTTP status + follow-up GET verification.
- **Advice**:
  - **DO** handle non-JSON preambles defensively.
  - **DO** verify by refetching the updated object (`GET ?context=edit`) after POST.

---

## The hardest class of bugs: duplication & drift

Duplication happened whenever we applied “patches” to content that was already patched, especially when scripts were re-run.

### How duplication showed up
- **TOC duplication**: multiple table-of-contents blocks inserted (and sometimes not all linked anchors worked).
- **CTA duplication**: landing page CTA repeated due to weak duplicate detection.
- **FAQ duplication/invisibility**: schema blocks existed but the frontend didn’t render questions; repeated fixes sometimes created multiple FAQ sections.
- **Image duplication**:
  - Same media ID reused across many posts (e.g., 2626 featured image issue).
  - Featured image duplicated as first in-body image (e.g., Rookie Day and others).
  - Two different images that are visually/semantically “duplicates” (same event theme).

### The solution pattern that worked best: rebuild from clean source
When we started from the current WordPress HTML and “patched,” we risked:
- repeated inserts,
- fragile regex matches,
- compounded formatting differences over time.

The **gold standard** approach was:
- **Start from clean, canonical source content** (JSON in `content/pages/` or `content/blogs/`),
- Rebuild with a consistent transformer,
- Upload once to WP,
- Verify in preview,
- Only then publish.

This is codified in scripts like:
- `rebuild_page_properly.py` (layout/spacing/images/boxes)
- `fix_*_complete.py` (robust page rebuilds from source JSON)

### Advice (anti-duplication)
- **DO** design scripts to be **idempotent** (safe to run repeatedly).
- **DO** use unique markers (CSS classes / block comments) for inserted elements.
- **DO** implement “remove existing X then add exactly one clean X” for:
  - TOCs
  - CTAs
  - FAQs
- **DON’T** “append another” unless you also “detect and remove old ones.”

See: `PAGE_ENHANCEMENT_GUIDELINES.md` for the idempotency rules we relied on.

---

## Source content ingestion: JSON encoding is not guaranteed clean

### The recurring issue
Some JSON files contained HTML that could break naive parsing (e.g., unescaped characters causing `JSONDecodeError`).

### How we overcame it
We implemented **robust extraction** strategies that:
- fall back to line-by-line parsing to isolate the `"content": "..."` field,
- avoid losing tail sections (common failure mode: “missing everything below the table”),
- ensure full HTML is preserved before processing.

This was critical for:
- `/a-day-at-camp/` (table + sections below)
- landing pages rebuilt into ACF blocks (`fix_water_sports_complete.py`, `fix_events_night_activities_complete.py`, `fix_what_to_expect_headings.py`)

### Advice
- **DO** validate that the extracted content contains expected sentinel headings/sections (e.g., last H2).
- **DO** compare length / section counts before and after extraction.
- **DON’T** assume `json.loads` will always succeed on “human-edited” JSON files.

---

## Landing pages: what made them uniquely complex

### Existence + replacement workflow matters
Landing pages frequently:
- already existed (and sometimes were live),
- needed “swap” behavior (replace old content with new approved content),
- needed draft review before going live.

The approved workflow became:
- **If published**: backup content, replace content, set to draft for review.
- **If already draft**: update draft content directly.

Supporting automation:
- `check_existing_pages.py` (existence/status)
- `update_landing_page.py` (workflow)
- backups written locally before any destructive update

### Template + block structure coupling
For “Our Story parity,” the biggest win was:
- converting to ACF blocks and setting the correct page template,
not only styling the HTML.

### The “missing H2 / unbroken content” issue
We hit a case where H2s existed in source but vanished after conversion. Root cause:
- faulty split/encode logic when building ACF content blocks.

Fix:
- `fix_what_to_expect_headings.py` rebuilt sections by splitting on actual `<h2>` tags and preserving them inside blocks.

### Advice (landing pages)
- **DO** treat headings as structural boundaries: split sections by H2 consistently.
- **DO** verify the rendered page has the expected H2 count and section breaks.
- **DON’T** ship raw HTML if the theme’s “gold standard” pages use ACF blocks.

---

## Blog posts: what made them uniquely complex

### Featured image vs first in-body image
WordPress themes often use featured image placement differently than the body.

We learned to enforce:
- Featured image is **unique per post** (avoid “same hero across all posts”).
- First in-body image should **not** be the featured image (avoid visual duplication).

Automation involved:
- scanning media metadata to select a relevant, unique featured image,
- replacing the first in-body image when it matches featured.

### Image alignment pitfalls (H2 wrapping)
Using `alignleft` caused text (including headings) to wrap around images in undesirable ways.

Fix:
- normalize images to `alignfull` + full-width styling for predictable flow.

### FAQ schema: correctness isn’t enough; it must render
We learned:
- A block can contain correct JSON-LD schema and still not show anything on the frontend if the theme/plugin expects specific markup.

Effective approach:
- Use a **simple visible HTML FAQ** (H2 + H3 + paragraphs) and embed schema in JSON-LD.
Scripts:
- `fix_faq_simple_visible.py`
- `fix_faq_remove_duplicates.py` (consolidate to exactly one)

### TOC: anchor IDs + duplicate removal are mandatory
TOC problems came from:
- repeated insertion,
- missing/duplicate heading IDs,
- brittle removal regex.

The stable pattern:
- remove all existing TOC variants aggressively,
- generate deterministic IDs for every H2,
- insert exactly one TOC in a single place.

---

## Internal links: timing and mapping strategy

### The challenge
Content used placeholders like `{{link:slug|anchor text}}`. Resolution is tricky because:
- some target pages may not be live yet,
- some slugs may map to unexpected pages (or not exist),
- drafts vs published URLs can differ based on site config.

Solution:
- build a slug→URL map from WordPress (`pages` + `posts`) and replace placeholders.
Script:
- `resolve_internal_links.py`

Advice:
- **DO** run link resolution when the target content set is stable (ideally after publishing).
- **DO** produce a report of unresolved slugs for manual review.
- **DON’T** silently map unknown slugs to an arbitrary page (better to leave placeholders + report).

---

## SEO metadata: update is easy; verification is not

### What worked
Updating Yoast fields via meta keys:
- `_yoast_wpseo_title`
- `_yoast_wpseo_metadesc`

Scripts:
- `add_seo_metadata_all.py`
- `verify_seo_metadata.py` (best-effort verification)

### What’s hard
Depending on WP/Yoast configuration, REST API may not reliably expose meta for readback, so verification sometimes requires:
- checking WP admin UI directly,
- confirming response codes and re-fetching with `context=edit`.

Advice:
- **DO** keep a local status file (IDs updated + timestamps).
- **DO** spot-check in WP admin after bulk updates.

---

## URL migration: redirects + menus are separate systems

We learned:
- Creating a new page + setting a 301 redirect solves **URL routing**, but not **navigation menus**.
- Menu items can still point to old pages until manually updated.

Reference:
- `MIGRATION_PLAN.md` (the correct sequence and why)

Advice:
- **DO** treat redirects, page creation, and menus as a 3-part migration.
- **DO** test with an incognito browser and with a redirect checker.

---

## “Don’t make the same mistakes again” (operational playbook)

### Golden workflow (safe, repeatable)
- **Step 0 — Backups**: export or locally store the current WP content before any destructive update.
- **Step 1 — Single-item test**: run scripts against one draft page/post and validate frontend + editor.
- **Step 2 — Rebuild > patch**: prefer rebuilding from clean source JSON over patching live content.
- **Step 3 — Idempotency**: every script must be safe to run twice without duplication.
- **Step 4 — Verification**:
  - verify via `GET ?context=edit`,
  - verify in WP editor (no block errors),
  - verify on the frontend preview (mobile + desktop).
- **Step 5 — Only then publish**.

### Common anti-patterns (avoid)
- **Patching unknown state**: editing whatever is currently in WP without ensuring it’s the canonical version.
- **Regex-first transformations** without strict markers and removal logic.
- **“Insert more” without “remove old”** (TOCs, FAQs, CTAs).
- **Assuming theme parity with raw HTML** when ACF blocks are the real driver.
- **Not validating completeness** (e.g., missing tail sections after tables).

---

## Practical checklists

### Landing page checklist (before publish)
- **Structure**
  - [ ] Page exists check done (avoid duplicates)
  - [ ] Correct page template set (if required by theme)
  - [ ] ACF block structure matches reference pages (if applicable)
  - [ ] H2 sections are present and visually separated
- **Layout**
  - [ ] Paragraph/headings spacing consistent (gold standard)
  - [ ] Images have consistent styling (e.g., `border-radius: 8px`) and spacing
  - [ ] CTA exists exactly once
- **Safety**
  - [ ] Old content backed up locally
  - [ ] Page set to draft for review (unless explicitly approved to publish)

### Blog post checklist (before publish)
- **Images**
  - [ ] Featured image is set and unique per post
  - [ ] First in-body image is not the featured image
  - [ ] In-body images are relevant and not visually repetitive
  - [ ] Images don’t cause heading wrap (prefer full-width)
- **FAQ**
  - [ ] Exactly 5 questions
  - [ ] Visible on frontend
  - [ ] Schema JSON-LD present
- **TOC** (only for long posts)
  - [ ] Exactly one TOC
  - [ ] All H2s have unique IDs
  - [ ] TOC links scroll correctly
- **SEO**
  - [ ] Yoast title + meta description set
- **Links**
  - [ ] No leftover `{{link:...}}` placeholders (or remaining ones are known/approved)

---

## Recommended future improvements (if you want this to be “production-grade”)

- **A single canonical “publisher” pipeline** per content type:
  - parse source → normalize → build blocks → insert media → insert FAQ/TOC → resolve links → upload → verify
- **A dry-run mode** that prints a diff summary (counts of H2, images, FAQs, TOC presence).
- **A “content contract” validator**:
  - ensures required sections exist before upload,
  - asserts no duplicates after upload.
- **Structured logs**: write a JSON log per run with post/page IDs, before/after counts, and verification results.

