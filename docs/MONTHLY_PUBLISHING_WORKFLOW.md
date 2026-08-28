# Monthly Publishing Workflow — HogEye Cameras

**Site:** https://hogeyecameras.com/ (WordPress)  
**Brand slug:** `hogeye-cameras`  
**Blog:** `/blog/`  
**Agent skill:** `.cursor/skills/he-monthly-cycle/SKILL.md` (load this every monthly cycle)

**Shared specs (canonical):** [Monthly content cycle](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/294943/Monthly+content+cycle) · [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684/Draft-first+CMS+publishing). This file is the HogEye implementation (WordPress commands, Schell/Casey/Lily, brand paths). Do not fork those shared rules here.

This is the **HogEye monthly cadence**: hub status → pull/apply → WordPress draft → confirm URLs → team email.  
The email reports what went to WordPress; it does not replace CMS publish.

Modeled on the Big Pig Traps loop, with **this repo’s WordPress publisher** (not Shopify).

Detail docs:

- Publish safety (local WP detail + hub pointer): `docs/PUBLISH_SAFETY_MANDATE.md`
- Publisher CLIs: `scripts/publisher/README.md`
- Voice / facts: `workspace/brand_truth/BRAND_BASELINE.md`
- Portal strategy: `SEO_STRATEGY.md`
- Operator setup: `docs/starter.md`

---

## Current gate (2026-08-24)

| Period | Hub | Site | Next |
| ------ | --- | ---- | ---- |
| **2026-07** | 5/5 **approved** | **Live** | Do not overwrite live URLs. `jul26_01` hub vs local content drift stays parked unless a live refresh is ordered. |
| **2026-08** | 4/5 **approved** (images on hub) | **WP drafts** (ids 500485–500488) | Schell done on hub. Lily publishes from WordPress when go-live is ordered. |
| **2026-09** | 5/5 **in_review** | not in WP | Schell copy review (5-post contract). Overflow parked repo-local (hub hidden). |
| **aug26_02** | Not on hub | HOLD | Mini Starlink price / buy path. |

Hub Approved ≠ live. Do not re-ingest after `--apply`. Status email sent 2026-08-24.

---

## Monthly loop (one cycle)

```text
Check hub status for YYYY-MM
        │
        ├─ approved  → pull --check/--apply/--check clean
        │                    │
        │                    ▼
        │              WP draft (required) → confirm URLs
        │                    │
        │                    ▼
        │              live only with explicit gate
        │
        └─ in_review → skip CMS; note Schell / Lily blockers
        │
        ▼
Team email draft (reports CMS result; does not replace publish)
        │
        ▼
Stop until send confirmation
        │
        ▼
Update Current gate + READY_FOR_REVIEW checkboxes
```

## Required path (do not skip)

1. Check hub status for period `YYYY-MM`
2. If approved → `pull --check` → `--apply` → `--check` clean
3. Push approved content to WordPress (draft-first; live only with explicit gate). Do **not** use BPT Shopify commands.
4. Confirm draft/live URLs
5. Create Schell/Casey/Lily Gmail DRAFT (no em dashes) summarizing what shipped + what is still `in_review`
6. Stop; do not send email unless asked

When **starting** a new month (research → hub, before the required path above):

```text
Research lock → briefs → drafts → READY_FOR_REVIEW
        │
        ▼
push:content (in_review) → expand if thin → re-push
        │
        ▼
Then the required path (hub status → apply → CMS → email)
```

---

## Phase checklist

### 0. Preflight

- [ ] `.env` has `DASHBOARD_URL`, `WD_INGEST_KEY`, `WD_BRAND=hogeye-cameras`, `WP_*`
- [ ] `client.config.json` expected URL/host is hogeyecameras.com
- [ ] If hub API 401: refresh `WD_INGEST_KEY` from the production ingest secret (working sister-brand `.env`, or wrangler `INGEST_KEY`). Dashboard `.dev.vars` is local-dev only. Do not invent keys.
- [ ] `./.venv/bin/python scripts/publisher/test_connection.py` before WP writes

### 1. Check hub status for `YYYY-MM`

```bash
npm run pull:approved -- --period=YYYY-MM
```

Report approved count, in_review count, missing images, drift vs local `externalId`s.

If nothing is approved: say so and continue to email / waiting-state work. **Do not publish.**

### 2. If approved: pull → check → apply → check again

```bash
node scripts/pull-approved.mjs --check --period=YYYY-MM
node scripts/pull-approved.mjs --apply --period=YYYY-MM
node scripts/pull-approved.mjs --check --period=YYYY-MM   # must exit clean
```

**Hard rules:** follow [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684/Draft-first+CMS+publishing) (Approved ≠ live; no re-ingest after `--apply`; create-only unless an exact live-URL refresh was ordered). Hub body is source of truth for title / slug / body / keyword until publish.

### 3. WordPress draft-first (required)

Do not skip when hub items are approved and not yet in WP. Honor `READY_FOR_REVIEW.md` publish priority when present.

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py \
  content/posts/<id>_wp_draft.json --type posts --status draft
```

Live only after Schell sign-off + preview + explicit user ask:

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py \
  content/posts/<id>_wp_draft.json --type posts --status publish --approved-in-dashboard
```

`--yes` does **not** bypass the dashboard approval gate.

**Safety:** [Draft-first CMS publishing](https://allgreatthings-44087732.atlassian.net/wiki/spaces/MFS/pages/65684/Draft-first+CMS+publishing) + HogEye sequence in `docs/PUBLISH_SAFETY_MANDATE.md`. AIOSEO fields for this stack: `meta_title` / `meta_description` / `focus_keyword`. Lily hub images are source of truth when present.

### 4. Parallel tech (while waiting)

Safe without Schell copy approval:

- `/trap-camera/` 404 → `/steel-camera/`
- H1 / meta template gaps
- Restore 404 blog slugs that live posts already link
- `/buy-now/` depth + GA4 tagging

Log notes under `work/seo/` or `workspace/technical_seo/`.

### 5. Hub Strategy + Overview

When strategy or language rules changed:

```bash
npm run push:strategy
```

- Strategy tab ← `SEO_STRATEGY.md`
- Overview tab ← `workspace/brand_truth/BRAND_BASELINE.md` via `/api/ingest/strategy` with `externalId=brand-baseline` and `category=baseline`

Overview ≠ Strategy.

### 6. Team email (every cycle)

Write this **after** the CMS push. The email reports WP draft/live URLs; it does not replace publish.

Create a **Gmail draft** (send only if the user asks).

| Field | Value |
| ----- | ----- |
| To | schell@clearmark.io, casey@tictactoemarketing.com |
| Cc | lily@tictactoemarketing.com |
| Style | No em dashes. Hyphens / commas / "then". |

Include:

1. Hub links: `?tab=strategy`, `?tab=overview`, `?tab=content`
2. What shipped live (with URLs)
3. What is `in_review` or approved-not-live + publish priority
4. **Lily:** after Schell approves on the hub, Lily adds featured images in **WordPress** and **publishes** (same as other WD brands). For August, hub images are already approved; Lily publishes the WP drafts when go-live is ordered.
5. Still-open items (approvals, parked SOPs, product facts)

Hub base:  
`https://wildlife-dominion-dashboard.jason-17f.workers.dev/brand/hogeye-cameras`

### 7. Close the loop

- [ ] Update **Current gate** in this file and `docs/HOGEYE_PROJECT_STATUS.md`
- [ ] Tick `READY_FOR_REVIEW.md` / monthly `STATUS.md` / `CONTENT_PLAN.md` checkboxes
- [ ] Confirm live URLs under hogeyecameras.com

### 8–12. New month (when starting the next cycle)

- [ ] Lock calendar + cuts with evidence (`workspace/SEO_STRATEGY_JUL_DEC_2026.md` + monthly `CONTENT_PLAN.md`)
- [ ] Briefs under `workspace/content_pipeline/monthly/YYYY-MM/briefs/`
- [ ] Drafts → `content/posts/<mon26>_NN_wp_draft.json` with stable `externalId`
- [ ] Write `workspace/content_pipeline/monthly/YYYY-MM/READY_FOR_REVIEW.md`
- [ ] `npm run push:content -- --period=YYYY-MM` (status `in_review`)
- [ ] Expand thin drafts and re-push **only while still `in_review`**
- [ ] Unique vs BB / BPT, especially screwworm
- [ ] Do not invent Mini AI / unreleased product facts

---

## Artifact map (per month)

| Artifact | Path |
| -------- | ---- |
| Content plan | `workspace/content_pipeline/monthly/YYYY-MM/CONTENT_PLAN.md` |
| Briefs | `workspace/content_pipeline/monthly/YYYY-MM/briefs/` |
| Markdown drafts | `workspace/content_pipeline/monthly/YYYY-MM/drafts/` |
| Post JSON | `content/posts/<mon26>_NN_wp_draft.json` |
| Review index | `workspace/content_pipeline/monthly/YYYY-MM/READY_FOR_REVIEW.md` |
| Strategy (portal) | `SEO_STRATEGY.md` |
| Baseline (portal Overview) | `workspace/brand_truth/BRAND_BASELINE.md` |
| Parallel tech notes | `work/seo/` + `workspace/technical_seo/` |

---

## Roles

| Who | Owns |
| --- | ---- |
| Agent / AGT | Research, drafts, push, pull/apply, WP draft→live, strategy/baseline sync, email draft |
| Schell | Hub copy + image approval |
| Lily | WordPress: featured images on posts, publish live |
| Casey | Team visibility / Tic Tac Toe marketing |

---

## Command cheat sheet

```bash
# Hub
npm run push:content -- --period=YYYY-MM
npm run push:strategy
npm run pull:approved -- --period=YYYY-MM
node scripts/pull-approved.mjs --check --period=YYYY-MM
node scripts/pull-approved.mjs --apply --period=YYYY-MM

# WordPress
./.venv/bin/python scripts/publisher/test_connection.py
./.venv/bin/python scripts/publisher/publish_content_item.py content/posts/<file>.json --type posts --status draft
./.venv/bin/python scripts/publisher/publish_content_item.py content/posts/<file>.json --type posts --status publish --approved-in-dashboard
```

---

## What to avoid

- Shopify `publish-shopify.mjs` commands (BPT only)
- Re-ingest after `--apply`
- Publishing live without Schell + preview + explicit ask
- Silent overwrite of an existing WP slug
- Auto-inserting images
- Em dashes in client emails
- Inventing Mini AI packaging/price/name
- Copying screwworm angles from Boar Blanket or Big Pig Traps
- Treating hub Approved as live
