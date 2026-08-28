# Google Doc — June 2026 batch (client review)

**Status (2026-05-19):** All five articles + executive summary pushed to the strategy Google Doc. **Sent to Schell for approval.** Do **not** push to WordPress until approved.

**Package status:** [`../STATUS.md`](../STATUS.md)

## Document

[Hog Eye | 2026 SEO Strategy & Blueprint](https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit)

## Tab mapping

| Google Doc tab | `article_id` | Repo file |
| --- | --- | --- |
| **May 2026** (cover) | — | `COVER_PAGE_EXECUTIVE_SUMMARY.md` |
| Article 1 | `jun26_02` | `Article_01_trapping_wild_hogs_texas.md` |
| Article 2 | `jun26_01` | `Article_02_hog_trap_placement.md` |
| Article 3 | `jun26_05` | `Article_03_electronic_hog_traps.md` |
| Article 4 | `jun26_03` | `Article_04_multi_trap_operation.md` |
| Article 5 | `jun26_04` | `Article_05_wild_hog_damage_field_guide.md` |

**Note:** Tab order (Article 1–5) does not match `jun26_01`–`jun26_05` numeric order — use the table above.

## Push commands

```bash
npm run google:push-tabs -- --month 2026-06              # overview + all articles
npm run google:push-tabs -- --month 2026-06 --overview   # May 2026 tab only
npm run google:push-tabs -- --month 2026-06 --no-overview   # articles only
npm run google:push-tabs -- --month 2026-06 --article jun26_01
```

## Editorial pass (completed before Schell send)

- Concrete field language (rooting, trails, wallows — not “active sign”)
- **Trigger** not release; human intros; no “Article N” meta
- Article 2: **How to Read Hog Signs**; wallows **(mud holes)** on first use
- Agent review: gpt-5.5 — see `../review/BATCH_AGENT_SUMMARY.md`

## After approval

1. Apply Schell edits in these files (or merge from Doc).
2. Sync to `../drafts/jun26_*_draft.md`.
3. Humanizer + QA → WP JSON → draft publish in June window.
