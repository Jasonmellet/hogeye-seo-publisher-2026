# Article pipeline tracker

**Owned by:** Librarian + operators (Cursor agents update this when status changes).  
**Last updated:** 2026-05-19 (may26 published 2026-05-04; jun26 sent to Schell — awaiting approval, no WP draft yet)  
**Companion:** `workspace/CONTENT_REGISTRY.md` (titles, clusters, links) — this file is the **operational stage** from idea → WordPress.

---

## Stages (single “current stage” per row)

Use **one** value in `pipeline_stage` — first match wins left-to-right:

| Stage | Meaning |
|-------|--------|
| `planned` | Topic only; no brief yet |
| `briefed` | Brief exists |
| `drafted` | Markdown draft exists |
| `qa` | QA artifact in progress or blocking |
| `gdoc_review` | In Google strategy / client doc for comments |
| `client_approved` | Client signed off on copy for this drop (comments resolved or explicit OK) |
| `wp_json` | `content/posts/*_wp_draft.json` (or equivalent) built from draft |
| `wp_draft` | Post exists in WordPress as **draft** (not public) |
| `published` | Live URL (see `workspace/SITEMAP_LIVE.md` for last crawl) |
| `revise` | Live post; copy change in flight (merge Doc → draft → JSON → WP update) |

**WP preflight (manual checklist):** Humanizer + `docs/agents/AGENT_SEO_MONITOR.md` Gate, `DRY_RUN` check, slug collision / **update vs create** decision before any REST push.

---

## April 2026 — `apr26_01` … `apr26_05`

| article_id | pipeline_stage | WP / URL notes | Client / Doc notes | Updated |
|------------|----------------|----------------|-------------------|---------|
| `apr26_01` | `published` | Live **2026-04-13** — `/net-hog-trap-workflow-how-to-monitor-verify-and-trigger-at-the-right-time/` | **2026-04-22:** Open-only archive refreshed (`latest-open-only.json`). Working digest for this piece: `drafts/_google_comments_open_apr26_01.md`. YouTube thread closed in Doc → merge remaining anchors into `drafts/apr26_01_draft.md` → regen `content/posts/apr26_01_wp_draft.json` → **revision** preflight. | 2026-04-22 |
| `apr26_02` | `published` | Live **2026-04-13** — cellular weak-coverage SOP slug | Resolve open Doc threads → `revise` when editing | 2026-04-22 |
| `apr26_03` | `published` | Live **2026-04-13** — remote readiness slug | Schell “good to go 4/20” in archive; close threads in Doc when merged | 2026-04-22 |
| `apr26_04` | `published` | Live **2026-04-13** — gate trigger setup slug | Await Schell ack on rewrite ping if still open | 2026-04-22 |
| `apr26_05` | `published` | Live **2026-04-13** — drop trap slug | Schell length + cross-link note; merge then `revise` | 2026-04-22 |

*Queue CSV `monthly_queue.csv` may lag; **this table + SITEMAP_LIVE** win for “is it live?”*

---

## May 2026 — `may26_01` … `may26_05`

| article_id | pipeline_stage | WP / URL notes | Client / Doc notes | Updated |
|------------|----------------|----------------|-------------------|---------|
| `may26_01` | `published` | Live **2026-05-04** — feral hog damage costs | May publication batch (5 posts) | 2026-05-19 |
| `may26_02` | `published` | Live **2026-05-04** — wild hog behavior | May publication batch | 2026-05-19 |
| `may26_03` | `published` | Live **2026-05-04** — hog trap baiting guide | May publication batch | 2026-05-19 |
| `may26_04` | `published` | Live **2026-05-04** — common hog trap mistakes | May publication batch | 2026-05-19 |
| `may26_05` | `published` | Live **2026-05-04** — corral vs box vs drop net | May publication batch | 2026-05-19 |

---

## June 2026 — `jun26_01` … `jun26_05` (created May, publish target June)

| article_id | pipeline_stage | WP / URL notes | Client / Doc notes | Updated |
|------------|----------------|----------------|-------------------|---------|
| `jun26_02` | `gdoc_review` | Not built | **Google Doc Article 1** — sent Schell 2026-05-19; agent GO (conditional) | 2026-05-19 |
| `jun26_01` | `gdoc_review` | Not built | **Google Doc Article 2** — sent Schell 2026-05-19; agent GO | 2026-05-19 |
| `jun26_05` | `gdoc_review` | Not built | **Google Doc Article 3** — sent Schell 2026-05-19; agent GO | 2026-05-19 |
| `jun26_03` | `gdoc_review` | Not built | **Google Doc Article 4** — sent Schell 2026-05-19; agent GO | 2026-05-19 |
| `jun26_04` | `gdoc_review` | Not built | **Google Doc Article 5** — sent Schell 2026-05-19; agent GO | 2026-05-19 |

---

## How agents should update this file

1. When **stage** changes, edit the row and bump **Last updated** (top) and row **Updated** date.  
2. When **Google Doc** threads close or new feedback arrives, refresh **`npm run google:archive-comments-open`** and **`npm run google:archive-suggestions`** (or **`npm run google:archive-doc-review`**) and summarize in **Client / Doc notes** if it changes what ships.  
3. After **WordPress** action, point to live URL or draft ID in **WP / URL notes**.
