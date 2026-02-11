# HogEye - Fast Track Runbook (to BB-level execution)

This runbook turns “discovery” into **tasks you can check off**. The goal is to reach:

- Month 1 plan (5 new + 5 updates)
- Briefs
- AI drafts (local)
- Staged WordPress drafts (one at a time)

---

## Non-negotiables (alignment + safety)

- **North Star**: every plan/brief/draft must align to the “wild hog trap release camera system” positioning in `work/seo/hogeye/NORTH_STAR_POSITIONING.md`.
- **Verified links only**:
  - HTML pages must come from a sitemap inventory (no guessing).
  - PDFs are allowed only when explicitly provided/approved (exception to sitemap rule).
- **Human review format**: when something is “ready for the team”, export a `.docx` so headings/lists/spacing survive Google Docs import.

## BB -> HogEye checklist (quick)

- [ ] Fill `work/seo/hogeye/PROJECT_CONFIG.json` (site URL, internal links, blacklist, north star terms)
- [ ] Enforce `work/seo/hogeye/NORTH_STAR_POSITIONING.md` before briefs/drafts
- [ ] Run `python3 scripts/seo/hogeye_preflight.py` and fix any missing config/env values
- [ ] Run smoke tests (WP + DataForSEO)
- [ ] Pull baseline datasets (GSC/GA4 where available + Screaming Frog crawl export)
- [ ] Pick Month 1: **5 new + 5 updates** and record choices in `work/seo/hogeye/EXECUTION_STATUS.md`
- [ ] Write 10 briefs, then generate drafts **locally only**
- [ ] Publish to WordPress as **drafts**, **one piece at a time**, with human review each step

---

## 0) Environment setup

1) Create `.env`:

```bash
cp env.example .env
```

1) Fill in required keys:

- WordPress: `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- Google: `GOOGLE_APPLICATION_CREDENTIALS`, `SEO_SPREADSHEET_ID`
- DataForSEO: `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`
- AI (HogEye): `OPENAI_API_KEY` (optional until drafting phase)

---

## 1) Smoke tests

```bash
python3 scripts/test_connection.py
python3 scripts/seo/dataforseo_benchmark_rank_snapshot.py --project-root "$(pwd)" --max-keywords 5 --output-dir "work/seo/benchmark/smoke"
```

---

## 2) Baseline benchmarks

Best effort (works partially without Google):

```bash
python3 scripts/seo/run_benchmark.py --project-root "$(pwd)" --allow-partial --skip-gsc --skip-ga4
```

When GSC/GA4 is ready, rerun without skips.

---

## 2.5) Clone existing WP content (metadata-only source of truth)

Create/refresh a local snapshot of **all existing posts + pages** (metadata + copy as plain text) so new work can be checked for duplicates and changes can be verified over time.

```bash
python3 scripts/seo/hogeye_wp_clone_metadata.py --project-root "$(pwd)" --include-copy --include-copy-hashes
```

---

## 3) Pull the missing datasets

- **GSC**:
  - Run `scripts/seo/gsc_benchmark_pull.py` once you have access.
- **DataForSEO**:
  - Run rank snapshots + SERP competitor snapshots using the existing benchmark scripts.
- **Screaming Frog** (manual):
  - Export crawl results and save them in your agreed location (either committed, or stored in Drive).
  - Capture *where* they live in `work/seo/hogeye/EXECUTION_STATUS.md`.

---

## 4) Month 1 plan (5 new + 5 updates)

- Pick 5 new topics based on:
  - GSC gaps + SERP opportunities
  - minimal cannibalization risk
  - clear intent and conversion path
- Pick 5 update targets based on:
  - high impressions + low CTR
  - pages with ranking potential (pos 6–20)

Record the chosen items (title, slug, target keyword, rationale) in `work/seo/hogeye/EXECUTION_STATUS.md`.
Every item must pass the North Star test in `work/seo/hogeye/NORTH_STAR_POSITIONING.md`.

---

## 5) Briefs

- Produce 10 briefs (5 new, 5 updates).
- Human spot-check each brief for intent, outline quality, and any claims that need sourcing.

---

## 6) AI drafts (local-only first)

- Generate ONE piece locally + review packet.
- Only after it passes validation and a human review, publish as a WP draft.

See `work/seo/hogeye/SAFETY_WORKFLOW.md`.

---

## 6.5) Export “important docs” to `.docx` for team review

This converts a curated set of alignment docs (README/runbooks/plans/North Star) into Google-Docs-friendly `.docx`.

```bash
./.venv/bin/python scripts/seo/export_alignment_docx.py
```

Edit the curated list here (keep it tight):

- `work/seo/hogeye/IMPORTANT_DOCS_MANIFEST.txt`

## 7) Staged WordPress drafts

- Publish **one piece at a time** as draft.
- For updates: require diff + backup approval before writing.
- Log each action (WP ID + URL) in the Hogeye audit log.

---

## Reference docs

- `work/seo/hogeye/PROGRESS_TRACKER.md`
- `work/seo/hogeye/SAFETY_WORKFLOW.md`
- `work/seo/hogeye/EXECUTION_STATUS.md`
