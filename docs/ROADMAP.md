# Camp Lakota Ops Engine — Roadmap

This repo supports two parallel tracks:

1) **WordPress Publishing Engine** (content execution)
2) **SEO Planning Engine** (data-driven monthly plans + measurement)

---

## Now (Jan–Feb 2026): Execute Feb plan cleanly

- **Wave 1 (early Feb)**:
  - Homepage update (protect countdown markers)
  - Sleepaway hub update
  - Dates & Tuition intent cleanup
  - 2 new posts
- **Wave 2 (mid Feb)**:
  - Supporting updates + remaining 3 posts

Definition of done:
- Draft-first → review → publish
- Checklists completed in `Feb_2026_execution_checklists`
- Measurement entries updated in `Feb_2026_measurement_weekly`

---

## Next (Mar–May 2026): Repeatable monthly planning + shipping

- **Monthly plan generator**:
  - Input: Semrush / DataForSEO / sitemap inventory
  - Output: clusters → final 10 → briefs → checklists → measurement tabs
- **Rank tracking & reporting**:
  - Weekly keyword snapshot (positions / impressions / clicks)
  - MQL tracking alignment with content launches
- **Content system hardening**:
  - Better “protected content” markers for sensitive homepage sections
  - Safer page updates (scope-limited updates where feasible)
  - Standard rollback procedure (local backup + WP restore path)

---

## Later (2026): Dashboard + deeper entity coverage

- Dashboard layer (Sheets → Looker Studio or lightweight internal UI)
- Stronger competitor/serp-format enrichment
- Automated internal linking suggestions and cannibalization prevention

---

## Current status (as of 2026-01-20)

- [x] WordPress auth + permissions verified (`test_connection.py`)
- [x] Draft-first canonical publishing pipeline
- [x] Homepage countdown safety guardrails + local WP backups (`work/wp_backups/`)
- [x] Feb 2026 plan artifacts pushed into the planning Google Sheet
- [ ] Execute Feb Wave 1 + Wave 2 publishing runs
