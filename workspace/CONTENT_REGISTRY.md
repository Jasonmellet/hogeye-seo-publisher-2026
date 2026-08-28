# HogEye Content Registry
### Owned by: The Librarian | Last updated: 2026-05-19

This is the single source of truth for all HogEye content — published, in draft, in brief, or planned. Update this file whenever a piece changes status.

---

## How to Read This Registry

**Status codes:**
- `published` — live on hogeyecameras.com
- `wp-draft` — in WordPress as a draft, pending final approval
- `approved` — client-approved in Google Doc, not yet in WordPress
- `google-doc` — in Google Doc, awaiting client review
- `gdoc_review` — in Google Doc; sent to client (operational alias used in pipeline tracker)
- `draft` — written, not yet sent to client
- `brief` — brief complete, ready to draft
- `planned` — topic confirmed, brief not yet written
- `archived` — no longer active (pre-North Star or superseded)

**Topic clusters:**
`trap-operations` | `damage-driven` | `trap-selection` | `remote-closure` | `hog-management` | `regulatory` | `competitor-displacement`

**Google Doc ↔ repo:** Client comments often sit on the shared strategy doc below while drafts live under `workspace/` and `content/posts/`. Match each Drive comment’s **quoted snippet** to a **title** in the mapping table, then open the linked files.

---

## Google Doc ↔ repository (traceability)

**Primary client review & strategy doc** (margin comments, approvals):

| Doc | Google `file_id` | Edit link |
|-----|------------------|-----------|
| Hog Eye \| 2026 SEO Strategy & Blueprint | `1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y` | [Open in Google Docs](https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit) |

**Pull comments locally:** from repo root, `npm run google:doc-comments -- "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y"` (requires `GOOGLE_APPLICATION_CREDENTIALS` in `.env`).

**Open comments only (matches Google “open” filter):** `npm run google:doc-comments-open -- "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y"` — skips threads Drive marks resolved.

**Archive comments to disk (JSON):** `npm run google:archive-comments -- "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y"` writes `workspace/comment_archive/<file_id>/<timestamp>.json` and `latest.json` (overwrite `latest` each run; timestamped files keep history).

**Archive open-only:** `npm run google:archive-comments-open -- "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y"` also writes `latest-open-only.json` (and a timestamped `*-open-only.json`) while still refreshing the full `latest.json`.

**Archive suggesting-mode snippets (Docs API):** `npm run google:archive-suggestions -- "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y"` writes `workspace/comment_archive/<file_id>/suggestions-latest.json`, timestamped `suggestions-<ISO>.json`, and `SUGGESTIONS_LATEST.md` (text runs with `suggestedInsertionIds` / `suggestedDeletionIds`; complements Drive margin comments).

**Full local review bundle (default strategy doc):** `npm run google:archive-doc-review` runs open-only comments archive, suggestions archive, then writes **`workspace/comment_archive/<file_id>/REVIEW_BUNDLE_LATEST.md`** — **May publication batch** (`may26_01`–`may26_05`, folder `content_pipeline/monthly/2026-05/`): open comments whose anchor/body match those five titles, plus inline suggestions on the matching Docs tabs (e.g. `1: How Much Do Feral Hogs Cost You?`, `4: Common Hog Trap Mistakes`, `5: Corral Trap vs. …`). **Not** the earlier trap SOP batch (`apr26_*` in `2026-04/`).

**Whole strategy doc (all open comments + all tabs’ suggestions):** `npm run google:render-review-bundle-full -- "<file_id>"` or `npx tsx scripts/content-system/render_google_doc_review_bundle.ts --full` → **`REVIEW_BUNDLE_FULL.md`**.

**Render bundle only (no API):** `npm run google:render-review-bundle` / `google:render-review-bundle-full` rebuild from existing `latest-open-only.json` + `suggestions-latest.json`.

**After Schell approves in Google (canonical copy):** accept suggestions in the Doc if you are satisfied, then pull the **saved** tab text into the repo:  
`npm run google:export-tab-plain -- --tab "Wild Hog Behavior" --out workspace/content_pipeline/monthly/2026-05/drafts/_google_sync/may26_02_plain.txt` (adjust `--tab` to match the tab title substring; optional trailing doc id defaults to the strategy doc). Merge that plain export into the real `may26_*_draft.md` (headings, lists, frontmatter), then regenerate `content/posts/may26_*_wp_draft.json` with the existing markdown → JSON script.

### Piece → repo files (match Google “quote” to title)

| ID | Registry | Title to match in Google comments | Markdown draft | WP export JSON |
|----|----------|-----------------------------------|----------------|----------------|
| FEB-01 | February | Wild Hog Trap Camera System: Complete Field Guide | `workspace/february_package/blog_01_wild_hog_trap_release_camera_system.md` | *(when generated)* |
| FEB-02 | February | Sounder Capture Timing: Baiting and Conditioning Workflow | `workspace/february_package/blog_02_sounder_capture_timing.md` | *(when generated)* |
| FEB-03 | February | Trap Gate Trigger Camera Reliability in Weak Cell Coverage | `workspace/february_package/blog_03_trap_gate_trigger_reliability.md` | *(when generated)* |
| FEB-04 | February | Multi-User Trap Monitoring: No-Miss Remote Closure Protocol | `workspace/february_package/blog_04_multi_user_trap_monitoring.md` | *(when generated)* |
| FEB-05 | February | Trap Compatibility and Warranty: Choosing a Trap-Ready Camera System | `workspace/february_package/blog_05_trap_compatibility_and_warranty.md` | *(when generated)* |
| `apr26_01` | April table | Net Hog Trap Workflow | `workspace/content_pipeline/monthly/2026-04/drafts/apr26_01_draft.md` | `content/posts/apr26_01_wp_draft.json` |
| `apr26_02` | April table | Cellular Hog Trap Trigger Reliability | `workspace/content_pipeline/monthly/2026-04/drafts/apr26_02_draft.md` | `content/posts/apr26_02_wp_draft.json` |
| `apr26_03` | April table | Remote Hog Trap Trigger Readiness Standards | `workspace/content_pipeline/monthly/2026-04/drafts/apr26_03_draft.md` | `content/posts/apr26_03_wp_draft.json` |
| `apr26_04` | April table | Hog Trap Gate Trigger Setup | `workspace/content_pipeline/monthly/2026-04/drafts/apr26_04_draft.md` | `content/posts/apr26_04_wp_draft.json` |
| `apr26_05` | April table | Drop Trap for Hogs | `workspace/content_pipeline/monthly/2026-04/drafts/apr26_05_draft.md` | `content/posts/apr26_05_wp_draft.json` |
| `may26_01` | MAY-01 | How Much Do Feral Hogs Cost You? Damage by Crop, Region, and Herd Size | `workspace/content_pipeline/monthly/2026-05/drafts/may26_01_draft.md` | `content/posts/may26_01_wp_draft.json` |
| `may26_02` | MAY-02 | Wild Hog Behavior: What Time They Move, How They Scout, and Why It Affects Your Trap | `workspace/content_pipeline/monthly/2026-05/drafts/may26_02_draft.md` | `content/posts/may26_02_wp_draft.json` |
| `may26_03` | MAY-03 | The Hog Trap Baiting Guide: What Works, What Doesn't, and How Long to Wait | `workspace/content_pipeline/monthly/2026-05/drafts/may26_03_draft.md` | `content/posts/may26_03_wp_draft.json` |
| `may26_04` | MAY-04 | Common Hog Trap Mistakes (and How Remote Monitoring Fixes Most of Them) | `workspace/content_pipeline/monthly/2026-05/drafts/may26_04_draft.md` | `content/posts/may26_04_wp_draft.json` |
| `may26_05` | MAY-05 | Corral Trap vs. Box Trap vs. Drop Net: Which Hog Trap Is Right for Your Property? | `workspace/content_pipeline/monthly/2026-05/drafts/may26_05_draft.md` | `content/posts/may26_05_wp_draft.json` |

*If you later use **separate** Google Docs per article, add a column `article-specific doc URL` here and in the piece’s `handoff/*.md`.*

---

## Published Content (Live on hogeyecameras.com)

*Update this section when WordPress drafts are approved and go live.*

| # | Title | Slug | Status | Publish Date | Primary KW | Cluster | Inbound Links From |
|---|---|---|---|---|---|---|---|
| — | *(no pieces confirmed live yet — update as Feb/Mar/Apr content publishes)* | | | | | | |

**Core product pages (existing — not blog content):**

| Page | Slug | Notes |
|---|---|---|
| Trap Camera (main) | `/trap-camera/` | ⚠️ Not confirmed in sitemap — use `/net-camera-trap-remote-hog-trapping/` until resolved |
| Steel Camera | `/steel-camera/` | Product page |
| Net Camera Trap | `/net-camera-trap-remote-hog-trapping/` | Confirmed live product page — use as primary camera link |
| Camera Resources | `/camera-resources/` | Education/setup hub |
| **Big Pig Traps** | `/hog-traps/` | Corral trap product — same company as HogEye. Link whenever discussing trap setup costs or DIY trapping. |
| **Boar Blanket** | `/hog-traps/` | Soft net trap system — same company as HogEye. Link whenever discussing net traps or large-sounder intercept. |
| Buy Now | `/buy-now/` | Pricing/purchase |
| Comparison page | `/reolink-vs-vosker-vs-hogeye-off-grid-camera-comparison/` | Needs reframe — April update target |

---

## February 2026 Package

**Theme:** Remote Trap Operations Foundation  
**Status:** Drafted — confirm WP publish status and update rows below  
**Google Doc ↔ repo:** See [Google Doc ↔ repository (traceability)](#google-doc--repository-traceability) — match comment **quotes** to the **Title** column below, then open the mapped `workspace/february_package/blog_*.md` file.

| # | Title | Slug | Status | Primary KW | Cluster | Target Internal Links |
|---|---|---|---|---|---|---|
| FEB-01 | Wild Hog Trap Camera System: Complete Field Guide | `wild-hog-trap-release-camera-system` | draft | wild hog trap camera system | trap-operations | /trap-camera/, /steel-camera/, /camera-resources/ |
| FEB-02 | Sounder Capture Timing: Baiting and Conditioning Workflow | `sounder-capture-timing` | draft | sounder capture timing | trap-operations | /trap-camera/, FEB-01 |
| FEB-03 | Trap Gate Trigger Camera Reliability in Weak Cell Coverage | `trap-gate-trigger-reliability` | draft | trap gate trigger camera | remote-closure | /trap-camera/, /steel-camera/, FEB-01 |
| FEB-04 | Multi-User Trap Monitoring: No-Miss Remote Closure Protocol | `multi-user-trap-monitoring` | draft | multi user trap monitoring | trap-operations | /trap-camera/, FEB-01, FEB-02 |
| FEB-05 | Trap Compatibility and Warranty: Choosing a Trap-Ready Camera System | `trap-compatibility-and-warranty` | draft | hog trap camera warranty | trap-operations | /trap-camera/, /steel-camera/, /buy-now/ |

---

## March 2026 Package

**Theme:** Scale Trap Workflow Coverage  
**Status:** Planning only — briefs not yet written

| # | Topic | Slug | Status | Primary KW | Cluster |
|---|---|---|---|---|---|
| MAR-01 | Buyer criteria for hog trap camera with remote trigger | TBD | planned | hog trap camera with remote trigger | trap-operations |
| MAR-02 | Trigger timing by trap phase (baiting → conditioning → closure) | TBD | planned | sounder capture timing | trap-operations |
| MAR-03 | Low-latency trigger response in poor signal areas | TBD | planned | trap gate trigger reliability | remote-closure |
| MAR-04 | Multi-operator workflows for no-miss closure | TBD | planned | multi user trap monitoring | trap-operations |
| MAR-05 | Modified camera pitfalls vs trap-ready systems | TBD | planned | hog trap camera warranty | competitor-displacement |

---

## April 2026 Package — Trap-execution five-piece (`apr26_01`–`apr26_05`)

**Theme:** Trap execution reliability (monitor → verify → trigger → sounder capture)  
**Status:** Published to blog **2026-04-13** (see `SITEMAP_LIVE.md`). Pipeline: `content_pipeline/monthly/2026-04/`.  
**Google Doc ↔ repo:** [Traceability table](#google-doc--repository-traceability) — `apr26_*` drafts + `content/posts/apr26_*_wp_draft.json`; comments on the shared strategy doc use **quoted headings** to identify the piece.

**Why this is not “April research”:** Keyword pulls, transcript mining, and DataForSEO runs for this batch were done in **March 2026** (`trap_release_20260318_210051Z/`, `2026-03-keyword-universe/`, TJ transcript). The **`apr26_`** prefix and **`2026-04`** folder mean **April go-live month**, not “all work happened in April.”

| # | article_id | Live title | Primary KW | Slug (path segment) |
|---|---|---|---|---|
| 1 | `apr26_01` | Net Hog Trap Workflow | net hog trap | `net-hog-trap-workflow-how-to-monitor-verify-and-trigger-at-the-right-time` |
| 2 | `apr26_02` | Cellular Hog Trap Trigger Reliability | cellular hog trap trigger | `cellular-hog-trap-trigger-reliability-a-practical-weak-coverage-sop` |
| 3 | `apr26_03` | Remote Hog Trap Trigger Readiness Standards | remote hog trap trigger | `remote-hog-trap-trigger-readiness-standards-that-reduce-missed-closures` |
| 4 | `apr26_04` | Hog Trap Gate Trigger Setup | hog trap gate trigger | `hog-trap-gate-trigger-setup-latch-and-cable-sop-for-closure-confidence` |
| 5 | `apr26_05` | Drop Trap for Hogs | drop trap for hogs | `drop-trap-for-hogs-trigger-timing-decisions-that-improve-capture-quality` |

---

## May 2026 Package

**Theme:** Problem Awareness + Trap Operations Foundation  
**Status:** **Published 2026-05-04** — live on blog (`may26_01`–`may26_05`). Pipeline: `content_pipeline/monthly/2026-05/`.

**Calendar vs folder:** You may do this work **during April** on the wall calendar; **`2026-05` / `may26_*` still means the May publication batch**, same way `apr26_*` was researched in March but published in April.

| # | Title | Slug | Status | Primary KW | Vol | Cluster | Brief File | Target Internal Links |
|---|---|---|---|---|---|---|---|---|
| MAY-01 | How Much Do Feral Hogs Cost You? Damage by Crop, Region, and Herd Size | `feral-hog-damage-cost` | published | feral hog damage | 170/mo | damage-driven | `content_pipeline/monthly/2026-05/briefs/may26_01_brief.md` | MAY-04, MAY-05, /trap-camera/ |
| MAY-02 | Wild Hog Behavior: What Time They Move, How They Scout, and Why It Affects Your Trap | `wild-hog-behavior-trap-timing` | published | wild hog behavior | — | trap-operations | `content_pipeline/monthly/2026-05/briefs/may26_02_brief.md` | MAY-03, MAY-04, /trap-camera/ |
| MAY-03 | The Hog Trap Baiting Guide: What Works, What Doesn't, and How Long to Wait | `hog-trap-baiting-guide` | published | wild hog bait | 260/mo | trap-operations | `content_pipeline/monthly/2026-05/briefs/may26_03_brief.md` | MAY-02, MAY-04, /trap-camera/ |
| MAY-04 | Common Hog Trap Mistakes (and How Remote Monitoring Fixes Most of Them) | `common-hog-trap-mistakes` | published | hog trapping techniques | — | trap-operations | `content_pipeline/monthly/2026-05/briefs/may26_04_brief.md` | MAY-02, MAY-03, MAY-05, /trap-camera/ |
| MAY-05 | Corral Trap vs. Box Trap vs. Drop Net: Which Hog Trap Is Right for Your Property? | `hog-trap-comparison-corral-box-drop-net` | published | corral hog trap | 590/mo | trap-selection | `content_pipeline/monthly/2026-05/briefs/may26_05_brief.md` | MAY-02, MAY-03, MAY-04, /trap-camera/, /steel-camera/, /net-camera-trap-remote-hog-trapping/ |

---

## June 2026 Package

**Theme:** Operational Excellence + Texas/Regional Authority  
**Status:** **Sent to Schell for approval (2026-05-19).** Client-review copy in `content_pipeline/monthly/2026-06/google_doc/`; executive summary on **May 2026** Google Doc tab. WordPress draft **not** started.  
**Live status:** [`content_pipeline/monthly/2026-06/STATUS.md`](content_pipeline/monthly/2026-06/STATUS.md)  
**Calendar vs folder:** Work happens **in May** on the wall calendar; **`2026-06` / `jun26_*` = June publication batch** (same pattern as May posts published 2026-05-04).

| # | Title | Slug | Status | Primary KW | Vol | Cluster |
|---|---|---|---|---|---|---|
| JUN-01 | Hog Trap Placement: Where to Set Traps, How to Read Hog Signs, and What to Do Before You Bait | `hog-trap-placement-guide` | gdoc_review (Schell) | hog trap placement tips | — | trap-operations |
| JUN-02 | Trapping Wild Hogs in Texas: Regulations, Permits, and What Landowners Need to Know | `trapping-wild-hogs-texas` | gdoc_review (Schell) | feral hogs texas | 1,900/mo | regulatory |
| JUN-03 | How to Run a Multi-Trap Hog Operation Across a Large Property | `multi-trap-hog-operation` | gdoc_review (Schell) | multi trap hog operation | — | trap-operations |
| JUN-04 | What Does Wild Hog Damage Look Like? A Field Guide for Landowners | `wild-hog-damage-field-guide` | gdoc_review (Schell) | wild hog destruction | 20/mo | damage-driven |
| JUN-05 | Electronic Hog Traps Explained: How Remote Trigger Systems Work | `electronic-hog-traps-explained` | gdoc_review (Schell) | electronic hog trap | 40/mo | remote-closure |

**Google Doc tab order (client review):** Article 1 = JUN-02 (Texas), Article 2 = JUN-01 (placement), Article 3 = JUN-05 (electronic), Article 4 = JUN-03 (multi-trap), Article 5 = JUN-04 (field guide).

---

## July 2026 Package

**Theme:** Competitor Displacement + Authority Consolidation  
**Status:** Topics confirmed — briefs not yet written

| # | Title | Slug | Status | Primary KW | Vol | Cluster |
|---|---|---|---|---|---|---|
| JUL-01 | HogEye vs. JAGER PRO: Comparing Remote Trap Monitoring Systems | `hogeye-vs-jager-pro` | planned | jager pro hog trap | 390/mo | competitor-displacement |
| JUL-02 | The True Cost of Hog Removal: DIY Trapping vs. Hiring a Service vs. Remote Monitoring | `hog-removal-cost-comparison` | planned | wild hog removal | $14 CPC | damage-driven |
| JUL-03 | Feral Hog Control Methods Ranked: Shooting, Trapping, Toxicants, and Remote Monitoring | `feral-hog-control-methods` | planned | feral hog control | 2,400/mo | hog-management |
| JUL-04 | Wild Hog Deterrents: What Works, What Doesn't, and Why Trapping Beats Repellents | `wild-hog-deterrents` | planned | wild hog deterrent | 480/mo | damage-driven |
| JUL-05 | How Many Pigs Make a Sounder? Understanding Hog Group Behavior for Better Capture Rates | `how-many-pigs-in-a-sounder` | planned | sounder capture hogs | — | trap-operations |

---

## Keyword Coverage Map

*Use this to check for cannibalization before assigning keywords to new briefs.*

| Keyword | Piece assigned | Status |
|---|---|---|
| wild hog trap camera system | FEB-01 | draft |
| sounder capture timing | FEB-02 | draft |
| trap gate trigger camera | FEB-03 | draft |
| multi user trap monitoring | FEB-04 | draft |
| hog trap camera warranty | FEB-05 | draft |
| feral hog damage | MAY-01 | published |
| wild hog behavior | MAY-02 | published |
| wild hog bait | MAY-03 | published |
| hog trapping techniques | MAY-04 | published |
| corral hog trap | MAY-05 | published |
| feral hogs texas | JUN-02 | gdoc_review (Schell) |
| hog trap placement tips | JUN-01 | gdoc_review (Schell) |
| multi trap hog operation | JUN-03 | gdoc_review (Schell) |
| wild hog destruction | JUN-04 | gdoc_review (Schell) |
| electronic hog trap | JUN-05 | gdoc_review (Schell) |
| jager pro hog trap | JUL-01 | planned |
| wild hog removal | JUL-02 | planned |
| feral hog control | JUL-03 | planned |
| wild hog deterrent | JUL-04 | planned |
| sounder capture hogs | JUL-05 | planned |

---

## Brand Source Material Ingested

*Update when new brand materials are added to raw_content/ and processed by the Librarian.*

| Date | File | Type | Key extractions | Impact on style guide |
|---|---|---|---|---|
| — | *(none ingested yet)* | | | |

---

## Content Ideas Backlog

*Topics surfaced from research or ingest that don't yet have a brief.*

| Topic | Source | Priority | Notes |
|---|---|---|---|
| State-by-state hog trapping regulations (beyond Texas) | PAA research | Medium | Could be a series or a hub page |
| Hog trap ROI calculator | Strategic gap | Medium | Interactive tool or structured guide |
| Wild hog population maps by state | Competitive gap | Low | Authority piece, hard to monetise directly |
| How to handle a caught sounder (dispatch, transport) | PAA research | Low | Sensitive — verify legal/ethical framing first |

---

## Internal Link Master Map

*Full bidirectional link map. Update when new pieces publish.*

| From | To | Anchor text | Status |
|---|---|---|---|
| MAY-01 | MAY-04 | common hog trap mistakes | live |
| MAY-01 | MAY-05 | which trap type is right for your property | live |
| MAY-01 | /trap-camera/ | remote trap monitoring | live |
| MAY-02 | MAY-03 | how long hogs take to commit to bait | live |
| MAY-02 | MAY-04 | common trap mistakes | live |
| MAY-02 | /trap-camera/ | real-time trap monitoring | live |
| MAY-03 | MAY-02 | wild hog scouting behavior | live |
| MAY-03 | MAY-04 | baiting-related trap mistakes | live |
| MAY-03 | /trap-camera/ | remote monitoring alerts when hogs are at the bait | live |
| MAY-04 | MAY-02 | sounder conditioning and behavior | live |
| MAY-04 | MAY-03 | pre-bait timeline | live |
| MAY-04 | MAY-05 | matching trap type to sounder size | live |
| MAY-04 | /trap-camera/ | real-time monitoring and remote closure | live |
| MAY-05 | MAY-02 | sounder size and composition | live |
| MAY-05 | MAY-03 | conditioning the sounder to your trap | live |
| MAY-05 | MAY-04 | closing too early with the wrong count inside | live |
| MAY-05 | /trap-camera/ | remote monitoring that works with any trap type | live |
| MAY-05 | /steel-camera/ | HogEye steel camera | live |
| MAY-05 | /net-camera-trap-remote-hog-trapping/ | net trap monitoring | live |
