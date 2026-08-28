# HogEye monthly run prompt

Source twin: Boar Blanket `docs/HOGEYE_MONTHLY_RUN_PROMPT.md`.  
Paste the block below into a new chat in this repo when starting a monthly cycle.

---

Run the HogEye monthly cycle the same way we run Boar Blanket: close the prior month, produce the next month, then one truthful Gmail draft. Do not send the email unless I say send.

Read first, in this repo, and follow them:

1. `.cursor/skills/he-monthly-cycle/SKILL.md`
2. `docs/MONTHLY_PUBLISHING_WORKFLOW.md`
3. `docs/PUBLISH_SAFETY_MANDATE.md`
4. `workspace/brand_truth/BRAND_BASELINE.md` (facts win)
5. `SEO_STRATEGY.md`
6. This month’s `READY_FOR_REVIEW.md` / Current gate if present

This is **HogEye Cameras**, not Boar Blanket and not Big Pig Traps.

- Site: `https://hogeyecameras.com` (WordPress only, `/blog/`)
- Hub brand: `hogeye-cameras` (not `hogeye`)
- Hub: `https://wildlife-dominion-dashboard.jason-17f.workers.dev/brand/hogeye-cameras`
- Lens: cameras, monitoring, alerts, remote **gate** trigger / observation. Not BB landscape whole-sounder trapping. Not BPT drop/panel removal-at-scale.
- Audience: landowners / land managers. Never "ranchers". No security / surveillance / theft framing.
- Screwworm: unique vs BB and BPT. HE = monitoring gap / remote eyes. NWS on live animals, not feces. No treatment, no human symptoms.
- Do not invent Mini AI, Mini Starlink, or any unreleased price / buy path. If a fact is missing, `[NEEDS SOURCE]` or hold the slot.
- Never copy Shopify publish commands from Big Pig Traps.
- No em dashes in drafts or in the team email. Write ranges as words (5 to 10).

Contract (confirm in `SEO_STRATEGY.md` / roadmap before you invent a quota): July–August were 5 posts/month; September–December scale toward 10/month. 2–3 unique screwworm pieces when the month calls for them.

## Do this in order

Copy and tick:

```
HogEye month YYYY-MM run:
A. Close prior month
- [ ] A0 Preflight (.env: DASHBOARD_URL, WD_INGEST_KEY, WD_BRAND=hogeye-cameras, WP_*)
- [ ] A1 Hub status for PRIOR period (approved / in_review / images / drift)
- [ ] A2 If approved: pull --check → --apply → --check clean. NEVER re-ingest after apply.
- [ ] A3 If approved and not yet in WP: WordPress draft-first. Live only if I explicitly ask.
- [ ] A4 Confirm draft vs live URLs (curl public slugs). Hub Approved ≠ live.
B. Produce NEXT month
- [ ] B1 Archive SEO_STRATEGY.md to a dated file under work/seo/ before rewriting
- [ ] B2 SEO top-up research (DataForSEO / LLM cites / GSC / live URLs). HE lens only.
- [ ] B3 Lock the slot map + CONTENT_PLAN + briefs with stable external_id (never key by slug)
- [ ] B4 Hand-author drafts at brief word targets (do not land short). Review packets + READY_FOR_REVIEW
- [ ] B5 Validate (this repo’s brief/rubric scripts if present)
- [ ] B6 npm run push:content -- --period=YYYY-MM  (in_review only). push:strategy if Strategy changed.
C. Email
- [ ] C1 Gmail DRAFT only. To schell@clearmark.io and casey@tictactoemarketing.com. Cc lily@tictactoemarketing.com.
- [ ] C2 Stop. Do not send unless I say send.
- [ ] C3 Update Current gate + READY_FOR_REVIEW to match reality.
```

### Commands (this repo)

```bash
npm run pull:approved -- --period=YYYY-MM
node scripts/pull-approved.mjs --check --period=YYYY-MM
node scripts/pull-approved.mjs --apply --period=YYYY-MM

# WordPress
./.venv/bin/python scripts/publisher/test_connection.py
./.venv/bin/python scripts/publisher/publish_content_item.py \
  content/posts/<id>_wp_draft.json --type posts --status draft

# Next month to hub
npm run push:content -- --period=YYYY-MM
npm run push:strategy
```

If hub API 401: refresh `WD_INGEST_KEY` from the production ingest secret (working sister-brand `.env` or wrangler `INGEST_KEY`). Local dashboard `.dev.vars` is dev-only. Do not invent or print keys.

WP safety: create-only; unique draft slug if the live slug exists unless I order `--allow-update-existing`. No auto images. AIOSEO required (`meta_title`, `meta_description`, `focus_keyword`). Real category, never Uncategorized. Prefer explicit files, not the whole `content/posts/` tree.

### Research + copy

- Evidence before slots. Refresh what already ranks before net-new URLs when GSC says so.
- Unique title / slug / CTA vs BB and BPT, especially screwworm and deer-season.
- Exact focus keyphrase in title, SEO title, meta, first ~120 words, one H2.
- Agency dates: name the agency and link it in the same paragraph, or hedge.
- If you use tables, use Gutenberg `wp-block-table` with visible borders so the theme does not strip them.

### Lily and Schell (same as BB, say it once)

- Schell: copy approval on the hub, then **image approval** on the hub.
- Lily: after Schell approves the images, Lily adds them in **WordPress** and **publishes**.
- Hub path for images: HogEye Cameras → Content → period YYYY-MM.
- Do not ask Schell to re-approve a month that is already Approved.
- If images for the closing month are already approved, do not tell Lily to upload them again. Tell her to put those approved images on the WP drafts and publish.
- Do not write two sections that are the same WP job (“drafts for preview” plus “Lily upload then publish”).

### Email truth test

Write the draft only after the CMS work in this sitting. BPT-style prose, titled posts, clean hub URLs, no slug dump, no em dashes.

Before you write, answer: what is actually open?

- Closed month + images approved → Lily WP + publish. Schell is done with that month.
- Next month ingested → Schell reviews `in_review` only.
- Strategy: only say V2 / updated if you actually ran `push:strategy`.
- Shipped live: only public URLs that return 200.
- Still open: only real leftovers.

Subject pattern: `HogEye SEO update - [closed month] [status], [next month] in review`

Hub links: `https://wildlife-dominion-dashboard.jason-17f.workers.dev/brand/hogeye-cameras?tab=strategy|overview|content`

Start by checking hub status for the prior period and the next period, then tell me what is Approved vs in_review vs already live before you write anything or push WordPress.
