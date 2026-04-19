# WordPress draft publishing — replication guide

**Purpose:** Describe safe, repeatable WordPress draft publishing and the **governance layers** around it—so teams can onboard, hand off work, or replicate the pattern without tying the explanation to a single client name.

This document is **client-agnostic**: it uses generic roles (organization, reviewer, conversion funnel) and treats repository paths as **examples** from a markdown-first content system. Your fork may rename workflows or env vars; the **ideas** stay the same.

---

## Who this is for

| Audience | What they need from this file |
| --- | --- |
| **Editors & strategists** | How **SEO governance** and the **Librarian** loop relate to publishing—not only CLI commands. |
| **Operators** | Draft-first WordPress sync, internal links, optional LLM anchors, backups, preflight. |
| **Teams replicating the stack** | Two implementation styles: **TypeScript + markdown in git** (Part 1) and **Python + JSON content** (Part 2). |

---

## Related documentation (this repository)

Paths below are **this repo’s** filenames; adapt names if you fork.

| Topic | Path |
| --- | --- |
| WordPress commands & REST/CPT notes | `workflows/wordpress_publishing.md` |
| Internal links (sitemap allowlist, LLM vs heuristic) | `workflows/internal_links_llm.md` |
| SEO non-negotiables & doc index | `config/seo_content_governance.md` |
| SEO gates (embedded in editorial lifecycle) | `workflows/seo_strategy_workflow.md` |
| Librarian workflow (full procedure) | `workflows/theo_librarian_workflow.md` |
| Editorial stages | `workflows/editorial_workflow.md` |
| Content strategy (pillars, clusters, site fit) | `workflows/content_strategy_guardrails.md` |
| Research packet before outline (if used) | `workflows/dataforseo_research_workflow.md` |
| Pass/fail SEO checks | `templates/review/seo_strategy_rubric.md` |
| Primary funnel / assessment CTA (if configured) | `config/theo_quiz_funnel.md` |
| WordPress field mapping | `config/wordpress_fields.md` |

---

## Part A — The Librarian workflow (doctrine alignment)

Some organizations name this after the brand (e.g. a “Librarian” or “curator” workflow). The name is less important than the **function**: keeping **shared guidance** aligned with **authoritative source material** so every future brief and draft starts from the same doctrine.

### A.1 What the Librarian is

The Librarian is a **governance loop for durable knowledge**, not for shipping a single article.

- It updates **reusable layers**: brand voice, selected editorial config, prompts, and sometimes email or outreach guidance.
- It takes **signals** from a designated high-trust source—often **processed notes** from talks, interviews, or recordings (e.g. a `source-notes/` or `video-derived-notes/` tree)—and reconciles those signals with static docs that otherwise go stale.

It is **not** article creation, not raw transcription, not autonomous editing of approved content, and not a replacement for SEO checks or WordPress automation.

### A.2 Why it exists

| Problem | What the Librarian addresses |
| --- | --- |
| **Drift** | Brand and prompt docs lag behind how principals actually speak and decide. |
| **Inconsistent AI assistance** | If prompts and brand files disagree with the latest source notes, model-assisted drafts inherit the conflict. |
| **Silent contradiction** | Without a scheduled reconciliation, two “true” versions of the doctrine coexist (slides vs site vs prompts). |

The Librarian exists so **one aligned layer** feeds the editorial pipeline. Individual pieces still pass through normal briefs, SEO gates, and review.

### A.3 What it is for (scope)

**In scope (typical):**

- Knowledge or brand directories that define voice and positioning.
- Selected config that governs writing, evidence, or revision behavior.
- Prompts used for drafting and revision.
- Optional: outreach or email guidance when explicitly included.

**Out of scope (typical):**

- Canonical approved articles in `final/` (or equivalent).
- Active briefs and drafts—do not silently rewrite them in “librarian mode.”
- Ingestion/transcription/publishing **scripts**—behavior changes belong to engineering review.
- Anything that should stay a **per-article** decision (keywords, internal links to new URLs, WordPress metadata).

### A.4 How it works (audit → proposal → review → apply)

1. **Audit** — Compare new or updated source notes to candidate target docs. Output: drift, contradictions, stronger phrasing opportunities, proposed actions. (Often assisted by a dedicated audit prompt.)
2. **Proposal** — Write a **proposal** artifact (e.g. under `knowledge/alignment/proposals/`): sources reviewed, files affected, change type (add / strengthen / reconcile / remove / no change), rationale, confidence, space for reviewer notes. **No direct edits** to doctrine files yet.
3. **Review** — A human approves, narrows, or rejects by file and by change item.
4. **Apply** — Implement **only** approved items. Preserve document structure unless the approval explicitly requires otherwise.
5. **Log** — Record what shipped (e.g. under `knowledge/alignment/applied/`): proposal reference, files changed, accepted/rejected items, date, reviewer.

Everything is **proposal-first and human-approved**. That is the safety model: the Librarian is not a self-healing bot.

### A.5 Cadence (suggested)

- **Light pass** when new source notes land: audit against a small set of highest-impact docs.
- **Weekly batch**: group notes from the week and propose updates together.
- **Periodic wider pass**: reconcile brand, config, and prompt layers across a quarter to reduce accumulated drift.

### A.6 How the Librarian differs from other loops

| Loop | Focus |
| --- | --- |
| **Editorial workflow** | One piece: brief → draft → approval → `final/` → WordPress draft. |
| **Single-piece “injection” or refresh** | Upgrades **one** brief, draft, or ops doc against selected sources. |
| **Librarian** | Updates **shared** guidance so **all** future pieces inherit alignment. |
| **SEO strategy workflow** | Per-article search and strategy discipline (gates, rubric)—see Part B. |

---

## Part B — SEO strategy governance (the SEO “guide”)

SEO here means **strategy and discipline encoded in the lifecycle**, not a one-off keyword pass before publish.

### B.1 Purpose

- Make **search and content strategy decisions explicit** at defined gates—same seriousness as evidence rules and editorial approval.
- Avoid **keyword stuffing**, invented statistics for “search appeal,” and **automatic live publish** (unless your policy explicitly allows it elsewhere).
- Keep **thesis integrity** ahead of raw search volume when the two conflict.

Canonical rules for this repository live in `config/seo_content_governance.md`; stage-by-stage behavior in `workflows/seo_strategy_workflow.md`. The **rubric** (`templates/review/seo_strategy_rubric.md`) is the practical checklist.

### B.2 What SEO governance is not

- Not a substitute for editorial quality or voice review.
- Not the Librarian loop (Librarian updates **shared doctrine docs**; SEO governance records **each article’s** fit, research traceability, and on-page choices).
- Not autonomous publishing: draft-first and human promotion to live remain the default pattern this guide assumes.

### B.3 Embedded gates (thought leadership–style pieces)

Use the rubric sections at each gate. Names may vary; the logic is:

| Gate | When | What to satisfy (summary) |
| --- | --- | --- |
| **1 — Brief** | Before outline | **Strategy fit:** content pillar, category/taxonomy intent, thesis vs keyword volume. **Research integrity:** if your process uses an external research packet (keywords, SERP, intent), its path and your keyword choices are on the brief; decisions are defensible from that evidence, not only from volume. |
| **2 — Pre-final** | Before `final/` | **On-page:** title, slug, headings, FAQ discipline where required. **Internal links:** only to URLs you can verify (site allowlist, sitemap, or manual). **Conversion funnel** (if your program has a primary on-site assessment or lead path): piece should qualify and route readers appropriately—see your funnel config, not guessed copy. |
| **3 — WordPress handoff** | After draft create/update | Preview in CMS; SEO plugin fields (focus keyphrase, title, meta description) per site standard; featured image; confirm automated inline links and optional funnel CTA blocks match editorial intent. |
| **4 — Measurement (optional)** | When the release matters | Analytics / GTM / Search Console follow-up as your ops team defines. |

Gate 3’s **automation** side (fetching sitemap, resolving links, HTML body) is the **technical** content in Part C—not a substitute for Gate 1–2 decisions.

### B.4 Supporting practices

- **Content strategy guardrails** (`workflows/content_strategy_guardrails.md`): pillars, clusters, site fit, how pieces relate to each other—complements SEO gates.
- **Research workflow** (if used): e.g. `workflows/dataforseo_research_workflow.md`—produces a packet **before** outline for pieces that require SERP/keyword evidence.
- **Evidence rules**: factual discipline applies to SEO packaging too (`config/evidence_and_examples.md` in this repo).

### B.5 Records

The **brief** and **review notes** (or rubric checklist) are usually enough audit trail: pillar, packet path if applicable, keyword rationale, verified internal links, funnel alignment, and later WP SEO plugin completion.

### B.6 Prompt alignment

Workflow prompts for briefs, outlines, drafts, and revision should **reference** the same governance so models do not improvise SEO claims. See `workflows/seo_strategy_workflow.md` for the list of prompts this repo ties in.

---

## Part C — How the three layers fit together

| Layer | Role | Cadence |
| --- | --- | --- |
| **Librarian** | Align **shared** brand/config/prompts with **source-of-truth notes** | Periodic; when new notes batch lands |
| **SEO strategy** | **Per-article** gates: research traceability, on-page, links, funnel, then WP handoff | Every governed piece |
| **WordPress sync (below)** | Push **approved** markdown to REST as **draft**; optional internal-link and funnel automation | After `final/` (or your approval stage) |

Automation for internal links uses an **allowlist** (e.g. sitemap-derived URLs) and optional LLM assistance for natural anchors—it does **not** replace brief sign-off or verified-link discipline from Gate 2.

---

## Part D — TypeScript markdown pipeline (example: npm + REST)

This pattern fits repos that keep **canonical copy in markdown**, convert to HTML for the theme, and call WordPress REST from Node scripts.

### D.1 What “good execution” means

| Goal | Typical mechanism |
| --- | --- |
| Wrong-site guard | Committed `client.config.json` (expected URL/host) vs `WP_SITE_URL` preflight |
| Draft by default | Env flags and CLI default to draft; live promotion explicit |
| Consistent body | Markdown → HTML (e.g. `marked`) before REST `content`, unless debugging raw markdown |
| Internal links without guessed URLs | Sitemap-derived allowlist + optional LLM pass with **verbatim** phrase matching |
| Optional primary funnel CTA | Configurable block when your funnel URL is not already linked (env-controlled in this repo) |
| Recoverability | JSON backup before update |
| API robustness | Tolerate noisy responses; verify with `GET …?context=edit` after write |

### D.2 Setup (typical)

1. Node LTS; `npm install`.
2. `.env`: `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD` (Application Password).
3. `client.config.json`: expected site URL and host.
4. If content lives in a **custom post type**, set REST collection env to the type’s `rest_base` and ensure `show_in_rest` is enabled in WordPress.
5. For LLM assisted links: `OPENAI_API_KEY` and optional model env vars.
6. Run your connection test script (e.g. `npm run wp:test-connection`).

### D.3 Environment variables (illustrative)

Exact names vary by repo. This project uses examples such as:

| Variable | Role |
| --- | --- |
| `WP_REST_POST_COLLECTION` | REST segment after `/wp/v2/` for CPT content |
| `WP_POST_CONTENT_FORMAT` | HTML vs raw markdown for REST body |
| `WP_SITEMAP_URL` / corpus path | Sitemap source for link allowlist |
| `WP_INTERNAL_LINKS_MODE` | Heuristic vs LLM default for `--resolve-links` |
| `OPENAI_INTERNAL_LINKS_MODEL` | Model for LLM link pass |
| Funnel toggles | e.g. whether to append a default CTA block and which URL (see `config/theo_quiz_funnel.md` here) |
| `DEFAULT_AUTHOR`, `DEFAULT_CATEGORY` | Site user id and taxonomy slug |

### D.4 Recommended sync recipe

1. Refresh sitemap / link corpus on a sensible cadence.
2. Validate frontmatter if your repo requires it.
3. Create or update draft with flags your pipeline supports, e.g.:

```bash
npm run wp:create-draft -- --resolve-links --resolve-links-llm path/to/final/article.md
npm run wp:update-post -- --resolve-links --resolve-links-llm <postId> path/to/final/article.md
```

4. Complete Gate 3 in the CMS (preview, SEO plugin, image).

**Internal link safety (summary):** allowlist-only URLs; verbatim phrase insertion; fallback to heuristic linker if LLM fails. See `workflows/internal_links_llm.md`.

### D.5 Code map (this repository)

| Area | Location |
| --- | --- |
| Create / update | `scripts/create_wp_draft.ts`, `scripts/update_wp_post.ts` |
| Markdown → HTML | `scripts/wp_content_format.ts` |
| Internal links | `scripts/lib/internal_links.ts`, `scripts/lib/internal_links_llm.ts` |

*If this guide disagrees with scripts or `workflows/wordpress_publishing.md`, prefer the code.*

### D.6 Replication checklist — TypeScript pipeline

- [ ] `.env` and `client.config.json` target the intended environment.
- [ ] Connection test passes.
- [ ] REST collection matches how content is stored in WordPress.
- [ ] Sitemap refreshed before heavy internal-link automation.
- [ ] LLM keys set if using LLM link mode.
- [ ] Preview and SEO plugin fields completed after sync.
- [ ] SEO rubric / governance satisfied for the piece (`config/seo_content_governance.md`).

---

## Part E — Python JSON pipeline (alternate template)

Some organizations use a **shared Python library**, JSON content under `content/posts/`, and entry scripts such as `scripts/publisher/publish_content_item.py`. This is a **different** layout from Part D; paths like `packages/core_py/` appear in **those** templates.

### E.1 Good execution (typical)

| Goal | Mechanism |
| --- | --- |
| Wrong-site guard | `client.config.json` + preflight |
| Draft default | CLI / pipeline default status draft |
| Quality | Shared validators, transforms, Yoast/meta helpers |
| Backups | JSON snapshots before destructive updates |
| Robust API | Sanitize JSON; verify after write |

### E.2 Architecture (conceptual)

- Shared package: auth, REST client, pipeline, validators, Gutenberg-aware media handling.
- Repo root: `.env`, `client.config.json`, JSON content, Python entrypoints.

### E.3 Commands (illustrative)

```bash
./.venv/bin/python scripts/publisher/publish_content_item.py /path/to/content/posts/my-post.json --type posts
./.venv/bin/python scripts/publisher/publish_batch.py /path/to/content/posts --type posts
```

`DRY_RUN=true` often skips writes.

### E.4 Pipeline behavior (abbreviated)

- **Posts:** load JSON, transform content, media library integration, taxonomy resolution, SEO meta, upsert by slug, validate.
- **Pages:** often require existing slug; optional ACF block handling; protected content markers per client config.

### E.5 Safety and governance (shared intent)

- Draft-first; live publish explicit.
- Human review before bulk publish where your process requires it.
- Verified internal links only; preflight against wrong host.
- Idempotent patterns for TOC/CTA so re-runs do not duplicate blocks.

### E.6 Replication checklist — Python template

- [ ] Template includes shared publisher package and `client.config.json`.
- [ ] `test_connection` (or equivalent) passes.
- [ ] Content contract documented (fields, SEO meta, slugs).
- [ ] Team rules: draft → review → live only after approval.
- [ ] ACF or block themes: validate against a reference page if applicable.

### E.7 Authority (which codebase wins)

- **This repo (Part D):** TypeScript scripts and `workflows/wordpress_publishing.md`.
- **Python template:** `publish_pipeline.py` and CLI entry points in **that** repository.

---

## Closing

**Librarian** = align **shared doctrine** with **source notes**, on a schedule, with human approval.  
**SEO strategy** = **per-article** gates from brief through WordPress handoff, recorded in the rubric and brief.  
**Publishing** = **draft-first** technical push; internal links and funnel CTAs are **assistive** and **allowlisted**, not a substitute for editorial or SEO sign-off.
