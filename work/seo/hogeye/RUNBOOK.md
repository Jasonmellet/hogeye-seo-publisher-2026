# Hogeye - Fast Track Runbook (to BB-level execution)

This runbook turns “discovery” into **tasks you can check off**. The goal is to reach:
- Month 1 plan (5 new + 5 updates)
- Briefs
- AI drafts (local)
- Staged WordPress drafts (one at a time)

---

## 0) Environment setup

1) Create `.env`:

```bash
cp env.example .env
```

2) Fill in required keys:
- WordPress: `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- Google: `GOOGLE_APPLICATION_CREDENTIALS`, `SEO_SPREADSHEET_ID`
- DataForSEO: `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`
- AI: `ANTHROPIC_API_KEY`

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

## 7) Staged WordPress drafts

- Publish **one piece at a time** as draft.
- For updates: require diff + backup approval before writing.
- Log each action (WP ID + URL) in the Hogeye audit log.

---

## Reference docs

- `work/seo/hogeye/PROGRESS_TRACKER.md`
- `work/seo/hogeye/SAFETY_WORKFLOW.md`
- `work/seo/hogeye/EXECUTION_STATUS.md`

