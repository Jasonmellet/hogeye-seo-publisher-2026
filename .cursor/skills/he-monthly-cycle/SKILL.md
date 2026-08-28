---
name: he-monthly-cycle
description: >-
  Runs the HogEye Cameras monthly SEO content cycle end-to-end: hub status,
  pull-approved check/apply, WordPress draft-first publish, parallel tech,
  Strategy/Overview sync, and a Schell/Casey/Lily Gmail draft. Use when the
  user asks to run the monthly cycle, check hub approval, pull approved
  posts, publish to WordPress, update SEO Strategy or Brand Baseline, or
  draft a status email for hogeyecameras.com / hogeye-cameras.
---

# HogEye monthly cycle

Canonical playbook: `docs/MONTHLY_PUBLISHING_WORKFLOW.md`.  
Safety: `docs/PUBLISH_SAFETY_MANDATE.md` → shared [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684).  
Voice/facts: `workspace/brand_truth/BRAND_BASELINE.md`.  
Portal strategy: `SEO_STRATEGY.md`.  
Shared research bar: [SEO Research Module](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65663) + [DataForSEO quality bar](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/327752).  
Gap loop: [Repo vs hub gap check](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65786).  
Operator packaging: [Publisher operator patterns](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/327877).

**Platform:** WordPress (`hogeyecameras.com`) only. Never copy Shopify publish commands from Big Pig Traps.

**Hub slug:** `hogeye-cameras` (from `WD_BRAND` / `scripts/pull-approved.mjs`). Not `hogeye`.

**Research (Engine A / monthly top-up):** This repo **consumes** Advanced SEO Analysis niche-bundle outputs. Do not treat `scripts/seo/dataforseo_*` (benchmark snapshots / cluster enrich) as the $10 bar. Full sprint needs 250+ SERP (incl GSC extras), depth 20, 28+ ChatGPT with `force_web_search`, 45+ LLM mentions, 15+ on-page. Copy configs/outputs into dated `workspace/content_pipeline/research/` folders.

## Required path (do not skip)

Hub status → apply → CMS push → then team email. The email reports what went to WordPress; it does not replace that step.

1. Check hub status for period `YYYY-MM`
2. If approved → `pull --check` → `--apply` → `--check` clean
3. Push approved content to WordPress (draft-first; live only with explicit gate). Do **not** use BPT Shopify commands.
4. Confirm draft/live URLs
5. Create Schell/Casey/Lily Gmail **DRAFT** (no em dashes) summarizing what shipped + what is still `in_review`
6. Stop; do not send the email unless asked

If nothing is approved: skip apply/CMS, still draft the email with blockers, then stop.

## Phases (run in order; do not skip gates)

Copy and track:

```
Month YYYY-MM progress:
- [ ] 0. Preflight (.env + ingest key)
- [ ] 1. Check hub status (approved / in_review / drift)
- [ ] 2. If approved: pull check → apply → check again (required)
- [ ] 3. WordPress draft-first CMS push (required; do not skip)
- [ ] 4. Confirm draft/live URLs in WP
- [ ] 5. Team email draft (Gmail) reporting what went to CMS
- [ ] 6. Stop; do not send unless asked
- [ ] 7. Close the loop in Current gate / READY_FOR_REVIEW
```

Parallel tech and Strategy/Overview stay optional extras, never a substitute for step 3.

Full month (when starting a new cycle, not just status → email):

```
- [ ] 8. Lock calendar / research cuts
- [ ] 9. Briefs + drafts + READY_FOR_REVIEW
- [ ] 10. push:content (in_review) → expand + re-push if still in_review
- [ ] 11. Wait: Schell approve + Lily images
- [ ] 12. Repeat phases 1–3 for this month, then live only after explicit ask
```

### 0. Preflight

- `.env`: `DASHBOARD_URL`, `WD_INGEST_KEY`, `WD_BRAND=hogeye-cameras`, `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- `client.config.json` matches hogeyecameras.com
- `./.venv/bin/python scripts/publisher/test_connection.py` before any WP writes
- If hub API **401**: refresh `WD_INGEST_KEY` from the Wildlife Dominion dashboard production ingest secret (sister-brand `.env` that currently authenticates, or wrangler `INGEST_KEY`). Local dashboard `.dev.vars` is **dev-only**. Do not invent keys. Never commit `.env`.

### 1. Check hub status

```bash
npm run pull:approved -- --period=YYYY-MM
```

Also fetch `in_review` (same `/api/content?brand=hogeye-cameras` with `status=in_review`) so the report is complete.

Report: approved count, in_review count, missing images, drift vs local `externalId`s.

If nothing is approved: say so, continue to email / waiting-state work, **do not publish**.

**Hard rule:** Hub Approved ≠ live on hogeyecameras.com.

### 2. If approved: pull → check → apply → check again

```bash
node scripts/pull-approved.mjs --check --period=YYYY-MM
node scripts/pull-approved.mjs --apply --period=YYYY-MM
node scripts/pull-approved.mjs --check --period=YYYY-MM   # must be clean
```

- Hub is source of truth for title / slug / body / keyword until publish.
- After `--apply`, **NEVER** `npm run push:content` for those items (resets to `in_review`).
- Honor publish priority in that month’s `READY_FOR_REVIEW.md` when present.

If `--check` shows drift on a slug that is **already live**, stop and ask before `--apply` + `--allow-update-existing`. Default monthly path creates **new WP drafts**, it does not silently refresh live URLs.

### 3. Publish path (WordPress, this brand only) — required

Do not skip this step when hub items are approved and not yet in WP. Default: **draft**. Live only after Schell sign-off + preview + explicit user ask.

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py \
  content/posts/<id>_wp_draft.json --type posts --status draft
```

Batch (same safety defaults):

```bash
./.venv/bin/python scripts/publisher/publish_batch.py \
  content/posts --type posts --status draft
```

Prefer explicit files / period batch, not the whole `content/posts/` tree (it holds back-catalog).

Live (only when ordered):

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py \
  content/posts/<id>_wp_draft.json --type posts --status publish --approved-in-dashboard
```

`--yes` skips the clientName prompt only. It does **not** bypass the approval gate.

**WP safety (PUBLISH_SAFETY_MANDATE + hub Draft-first)**

- No silent overwrite. Collision → new unique slug unless `--allow-update-existing` or JSON `update_existing: true` was explicitly ordered. Stored `wp_post_id` alone is **not** opt-in.
- Never auto-insert images (`autoInsertImages: false`; CLI min/max images default 0). Lily on hub is source of truth when hub `images[]` exist.
- Always land SEO meta: `meta_title`, `meta_description`, `focus_keyword` on the WP draft (hard-fail). Body-only = failed publish. AIOSEO verify when `seoPlugin=aioseo`.
- Assign a real WP category (never Uncategorized).
- Verify: status=draft, category set, AIOSEO set, featured_media=0 unless Lily image was applied on purpose, no auto-inserted body images.

### 4. Parallel tech (optional, while waiting)

Safe on-page work that does **not** need Schell copy approval (redirects, 404 slug restores, H1/meta templates, `/buy-now/` depth). Log under `work/seo/` or `workspace/technical_seo/`. Skip product-claim edits and Mini AI / unreleased facts.

### 5. Strategy + Overview (if changed this cycle)

```bash
npm run push:strategy          # SEO_STRATEGY.md → hub Strategy tab
```

Brand baseline → hub **Overview** (not Strategy). POST `/api/ingest/strategy` with `externalId=brand-baseline` and `category=baseline`, body from `workspace/brand_truth/BRAND_BASELINE.md`. Overview ≠ Strategy.

### 6. Team email (every cycle) — Gmail DRAFT only

Write this **after** the CMS push. The email reports draft/live WP URLs; it does not replace publish.

- **To:** schell@clearmark.io, casey@tictactoemarketing.com
- **Cc:** lily@tictactoemarketing.com
- **Subject:** `HogEye SEO update - [prior] live, [month] in WordPress drafts, …`
- **No em dashes** anywhere in subject or body. Use hyphens, commas, or "then".
- **Style:** Match the Big Pig Traps team email. Greeting is "Hi Schell, Casey, and Lily,". Short labeled sections (Hub, Lily images, August drafts / shipped live, Still open). Titles and one-line asks, not numbered dumps of raw URLs. Link titles in HTML; never paste `google.com/url?q=` wrappers.

Include:

1. Hub Strategy / Overview / Content as titled links plus one sentence each
2. What shipped live (titles; blog root). Hub Approved is not live.
3. What went to WordPress (draft vs live) + publish priority as a short 1) → 2) → then the rest
4. Lily: same process as other WD brands; hub path `HogEye Cameras → Content → period YYYY-MM`
5. Still-open items (Lily WP publish, next-month hub review, Mini Starlink facts, parked tech)

Hub base: `https://wildlife-dominion-dashboard.jason-17f.workers.dev/brand/hogeye-cameras`

### 7. Close the loop

Update Current gate in `docs/HOGEYE_PROJECT_STATUS.md` and that month’s `READY_FOR_REVIEW.md` / `STATUS.md` / `CONTENT_PLAN.md` checkboxes to match reality.

## Non-negotiables

- WordPress only for this brand. Do not copy BPT Shopify commands.
- Unique vs Boar Blanket / Big Pig Traps (especially screwworm). HogEye = monitoring, alerts, remote trigger, observation. Not BB landscape trapping. Not BPT removal-at-scale ops.
- `workspace/brand_truth/BRAND_BASELINE.md`: landowners not ranchers; no security/surveillance positioning; no invented Mini AI / unreleased claims; NWS = live animals not feces.
- Never commit `.env` / tokens.
- Never publish live without user + Schell gate.
- No em dashes in client-facing emails.

## Quick commands

| Action | Command |
| ------ | ------- |
| Push drafts to hub | `npm run push:content -- --period=YYYY-MM` |
| Push strategy | `npm run push:strategy` |
| List approved | `npm run pull:approved -- --period=YYYY-MM` |
| Diff hub vs local | `node scripts/pull-approved.mjs --check --period=YYYY-MM` |
| Apply hub edits | `node scripts/pull-approved.mjs --apply --period=YYYY-MM` |
| WP connection | `./.venv/bin/python scripts/publisher/test_connection.py` |
| WP draft | `./.venv/bin/python scripts/publisher/publish_content_item.py content/posts/<file>.json --type posts --status draft` |
| WP live | same + `--status publish --approved-in-dashboard` |
