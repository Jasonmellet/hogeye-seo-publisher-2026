# Hogeye 2026 SEO Execution Status

**Last Updated:** 2026-06-23

## Purpose

This folder is the **single source of truth** for Hogeye’s SEO execution work:
- what data we’ve pulled
- what we’ve decided to build this month
- what has been drafted in WordPress
- what is still pending review/publish

---

## Current State (High level)

### Phase 1: Data & Baseline — **COMPLETE**

- [x] **Full audit sprint** migrated from Advanced SEO Analysis → `workspace/content_pipeline/research/sprint_20260622_audit/`
- [x] Screaming Frog June 2026 crawl → `work/seo/screaming_frog/2026.06.22.agt-cursor/`
- [x] GSC + GA4 pulls (through 2026-06-21) → `sprint_20260622_audit/inputs/gsc/`, `inputs/ga/`
- [x] DataForSEO $10-tier run ($7.08; 320 SERP, 45 LLM, 28 ChatGPT) → `sprint_20260622_audit/inputs/dataforseo/`
- [x] Synthesis docs → `sprint_20260622_audit/findings/`
- [x] Screaming Frog MCP configured (`.cursor/mcp.json` → `sf`)
- [x] Crawl comparison logged → `workspace/technical_seo/CRAWL_COMPARISON.md` (June 2026 row)
- [ ] Technical fix tracker triaged for **new** June findings (`workspace/technical_seo/TRACKER.csv`)

### Phase 2: Planning — **IN PROGRESS (July 2026)**

- [x] **6-month roadmap (Jul–Dec 2026)** → `workspace/SEO_STRATEGY_JUL_DEC_2026.md` (supersedes `SEO_STRATEGY_MAY_JUL_2026.md` for Jul+)
- [x] **July 2026 content plan** → `workspace/content_pipeline/monthly/2026-07/CONTENT_PLAN.md`
- [x] Queue seeded (5 posts) → `workspace/content_pipeline/monthly/2026-07/queue/monthly_queue.csv`
- [ ] Month 1 briefs approved by human
- [ ] Update targets for `/trap-camera/` redirect + buy-now (see CONTENT_PLAN technical table)
- [ ] Internal link targets confirmed against WP clone / sitemap

### Phase 3: Briefs

- [ ] 5 briefs written (`jul26_01` – `jul26_05`)
- [ ] Briefs reviewed by human (intent, outline, screwworm dedup vs BB/BP)

### Phase 4: AI Draft Generation (local-only)

- [ ] Research packs + drafts generated locally (no WordPress writes)
- [ ] All drafts PASS quality gates + humanizer

### Phase 5: Staged Publishing (WordPress drafts)

- [ ] Test publish 1 piece as draft
- [ ] Remaining pieces draft-only, one at a time

### Phase 6: Review → Publish Live

- [ ] Schell approval
- [ ] Publish approved drafts live

---

## Where to start (agents)

1. Read `workspace/content_pipeline/research/sprint_20260622_audit/INDEX.md`
2. Read `workspace/content_pipeline/monthly/2026-07/CONTENT_PLAN.md`
3. Enforce `workspace/NORTH_STAR_POSITIONING.md` before any brief/draft

---

## Known Risks / Guardrails

- **Draft-first always**: Nothing goes live automatically.
- **One-piece-at-a-time**: human approval before each WordPress write.
- **Screwworm dedup**: check `sprint_20260622_audit/stakeholder/screwworm-topic-matrix.md` before screwworm briefs.
- **No secrets in git**: `.env`, keys, service-account JSON stay uncommitted.

---

## Audit repo relationship

**Advanced SEO Analysis** (`clients/hogeye/`) = analysis engine.  
**This repo** = publishing + monthly pipeline. Re-import via new `sprint_*` folder when audit phases complete — do not plan calendars in the audit repo.
