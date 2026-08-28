# Content Requirements (HogEye Cameras)

What a finished post needs before it enters this repo's pipeline. This describes the
**publishable JSON shape** consumed by `scripts/publisher/publish_content_item.py` and the
authority docs that govern voice, facts, and strategy. It is not a generic intake form —
brand voice, facts, and topic/keyword/cadence authority already live in this repo.

---

## 1. Authority sources (read before drafting)

| Concern | Source of truth |
|---------|-----------------|
| Brand truth / orientation | `workspace/brand_truth/BRAND_BASELINE.md` |
| Approved / banned language | `workspace/brand_truth/APPROVED_LANGUAGE.yml`, `workspace/KEYWORD_BLACKLIST.md` |
| Truth hierarchy + owner overrides | `workspace/brand_truth/TRUTH_HIERARCHY.md`, `OWNER_RULES_OVERRIDE.md`, `CLIENT_FEEDBACK_SCHELL_APR2026.md` |
| Voice / structure / FAQ / CTA | `workspace/HOGEYE_CONTENT_STYLE_GUIDE.md`, `workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md` |
| Topics / keywords / cadence | `SEO_STRATEGY.md` (portal) + `workspace/SEO_STRATEGY_JUL_DEC_2026.md` (full roadmap) |
| Pre-submission QA | `workspace/PRE_SUBMISSION_QA_CHECKLIST.md` |

---

## 2. WordPress access (one-time per site)

Set in a gitignored `.env` (see `env.example`); never commit secrets.

- [ ] `WP_SITE_URL` (e.g. `https://hogeyecameras.com`)
- [ ] `WP_USERNAME`
- [ ] `WP_APP_PASSWORD` (WordPress Admin → Users → Profile → Application Passwords)

`client.config.json` records the expected site (`expectedWpSiteUrl`/`Host`/`Name`),
`seoPlugin: "aioseo"`, and internal-link aliases. The preflight hard-blocks publishing to a
mismatched site.

---

## 3. Per-cycle content packages

Editorial work lives under `workspace/content_pipeline/monthly/<YYYY-MM>/` (`briefs/`,
`research_packs/`, `drafts/`, `qa/`, `handoff/`). Each article package needs:

- [ ] `briefs/<article_id>_brief.md`
- [ ] `research_packs/<article_id>_research_pack.md`
- [ ] `drafts/<article_id>_draft.md` (final markdown; voice-checked, fact-locked)
- [ ] `qa/<article_id>_qa.md` (QA checklist passed)

The markdown draft is converted to publishable JSON by
`scripts/seo/hogeye_draft_md_to_post_json.py` → `content/posts/<id>_wp_draft.json`.

---

## 4. Post JSON fields (`content/posts/*.json`)

**Required:** `title`, `content` (HTML).

**Standard for HogEye posts:**
- `slug` — permanent identity (same slug updates in place on WP and the dashboard)
- `status` — default `draft`
- `excerpt`
- `meta_title` (primary keyword, < 60 chars), `meta_description` (140–155 chars)
- `focus_keyword`
- `categories` (existing WP category names — see `PROJECT_CONFIG.json`; do not auto-invent)
- `tags`
- `faq_items` — `[{ "question": "...", "answer": "..." }]` (4–6; rendered to AIOSEO FAQPage schema)

**Optional:** `featured_image` / `featured_image_alt`, `featured_media_id`, `date`,
`enable_toc`, `content_image_count`.

SEO fields map to AIOSEO (`aioseo_meta_data`) via `client.config.json`. Internal links use
`{{link:alias|anchor}}` placeholders (aliases from `client.config.json`), resolved at publish
with `--resolve-links`.

See a real example: `content/posts/may26_01_wp_draft.json`.

---

## 5. Images

- [ ] Files in the WP media library (the pipeline matches by keyword) or supplied IDs
- [ ] Descriptive `featured_image_alt` matching a trap/field scene (not a generic camera)
- Format JPG/PNG/WebP, ≥1200px wide, optimized (< ~500KB)

---

## 6. Approval & publishing

- [ ] Push finished posts to the Wildlife Dominion dashboard: `npm run push:content`
      (brand `hogeye-cameras`, status `in_review`).
- [ ] **Schell approval in the dashboard is required before going live.** The publish step
      is hard-blocked on `--status publish` unless dashboard approval is confirmed
      (`--approved-in-dashboard` or the interactive `APPROVED` prompt).
- [ ] Publish draft-first: `python3 scripts/publisher/publish_content_item.py <file> --type posts`
      (default `--status draft`), then flip to publish after the WP draft post-flight.

See `docs/MONTHLY_PUBLISHING_WORKFLOW.md` for the full sequence.
