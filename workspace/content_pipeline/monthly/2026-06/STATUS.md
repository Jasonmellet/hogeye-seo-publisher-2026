# June 2026 publication batch — project status

**Publication target:** June 2026  
**Work completed in repo:** May 2026  
**Last updated:** 2026-05-19  

**Package index:** `PACKAGE_INDEX.md`  
**Executive summary (Google Doc):** `google_doc/COVER_PAGE_EXECUTIVE_SUMMARY.md` → **May 2026** tab  
**Strategy:** `workspace/SEO_STRATEGY_MAY_JUL_2026.md` (June section)

---

## Current stage

| Milestone | Status |
| --- | --- |
| Briefs (5) | ✅ Complete |
| Research packs (5) | ✅ Complete |
| Client-review copy (`google_doc/`) | ✅ Complete + expanded |
| Agent batch review (gpt-5.5) | ✅ Complete — Articles 2–5 **GO**; Article 1 **GO (conditional)** |
| Executive summary cover page | ✅ Pushed to **May 2026** tab |
| All articles pushed to Google Doc | ✅ Article 1–5 sub-tabs |
| **Sent to Schell for approval** | ✅ **2026-05-19** |
| Schell approval received | ⏳ Pending |
| Merge Doc → `drafts/jun26_*_draft.md` | ⏳ After approval |
| WordPress JSON (`content/posts/`) | ⏳ After approval |
| WordPress **draft** posts | ⏳ **Not started** — do not push until Schell approves |
| Live publish (June target) | ⏳ After WP draft QA |
| Companion page updates (`PAGE_UPDATES_JUNE.md`) | ⏳ After articles approved / staged |

---

## Google Doc (client review)

**Document:** [Hog Eye \| 2026 SEO Strategy & Blueprint](https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit)

| Tab | Content |
| --- | --- |
| **May 2026** | Executive summary cover page |
| **Article 1** | Texas regulations (`jun26_02`) |
| **Article 2** | Hog trap placement (`jun26_01`) |
| **Article 3** | Electronic hog traps (`jun26_05`) |
| **Article 4** | Multi-trap operation (`jun26_03`) |
| **Article 5** | Wild hog damage field guide (`jun26_04`) |

**Re-push from repo:**

```bash
npm run google:push-tabs -- --month 2026-06 --overview     # May 2026 tab only
npm run google:push-tabs -- --month 2026-06               # overview + all articles
npm run google:push-tabs -- --month 2026-06 --article jun26_01   # single article
```

---

## Work log (May 2026)

1. Scaffolded June pipeline (`hogeye_create_monthly_pipeline.py --month 2026-06`).
2. Drafted five briefs + initial `google_doc/` articles.
3. Ran multi-agent review (`npm run agent:batch-review -- --month 2026-06`) on **gpt-5.5** against May approved corpus.
4. Expanded all five articles (field depth, North Star ties, concrete language pass).
5. Fixed voice issues: robotic intros, `active sign` → fresh rooting/trails, **trigger** not release, **hog signs** / **wallows (mud holes)** in Article 2.
6. Added editorial rules to `HUMANIZER_STYLE_GUIDE.md`, `HOGEYE_CONTENT_STYLE_GUIDE.md`, agent docs, and `agent_batch_review.ts` deterministic checks.
7. Pushed all tabs to Google Doc; added executive summary to **May 2026** tab.
8. **Sent package to Schell for approval** (2026-05-19).

---

## Agent review summary (gpt-5.5, post-revision)

See `review/BATCH_AGENT_SUMMARY.md` and `review/jun26_*_agent_review.md`.

| Doc tab | `article_id` | Google Doc |
| --- | --- | --- |
| Article 1 | `jun26_02` | GO (conditional) |
| Article 2 | `jun26_01` | GO |
| Article 3 | `jun26_05` | GO |
| Article 4 | `jun26_03` | GO |
| Article 5 | `jun26_04` | GO |

---

## Next steps (after Schell approval)

1. Archive Google Doc comments / suggestions (`npm run google:archive-doc-review`).
2. Merge approved copy from `google_doc/` → `drafts/jun26_*_draft.md`.
3. Humanizer + `PRE_SUBMISSION_QA_CHECKLIST.md` pass on merged drafts.
4. Build `content/posts/jun26_*_wp_draft.json` (draft-first).
5. Push to WordPress as **draft only** — no live publish until post-flight QA.
6. Execute `PAGE_UPDATES_JUNE.md` (hubs + GSC quick wins).
7. Update `CONTENT_REGISTRY.md` + `ARTICLE_PIPELINE_TRACKER.md` → `wp_draft` / `published`.

---

## Blockers

| Item | Notes |
| --- | --- |
| Schell approval | Waiting on client review |
| GSC API export | Service account project — enable Search Console API or manual export for page-update targets |
| June URLs not live yet | Internal links to `/hog-trap-placement-guide/`, `/electronic-hog-traps-explained/`, etc. validate at WP JSON build |

---

## Theme and goals

**Operational Excellence + Texas / Regional Authority**

- Capture Texas search demand (`feral hogs texas`).
- Deepen trap-operations SOP content (placement, electronic triggers, multi-trap, damage ID).
- Link forward from **May 2026 published batch** (behavior, baiting, mistakes, comparison, damage cost).
- Route readers to product hubs and remote monitoring outcomes (North Star).
