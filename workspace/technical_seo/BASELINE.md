# HogEye technical SEO baseline

## Current reference (June 2026)

**Source crawl:** `2026.06.22.agt-cursor`  
**Local exports:** `work/seo/screaming_frog/2026.06.22.agt-cursor/`  
**Written findings:** `workspace/content_pipeline/research/sprint_20260622_audit/findings/technical-findings.md`

## Historical baseline (April 2026)

**Source crawl:** `2026.04.09.05.15.26`  
**Evidence location (read-only):** `Advanced SEO Analysis/clients/hogeye/inputs/screaming_frog/2026.04.09.05.15.26/`

Use June 2026 as the **active comparison point** for fix work. Copy new crawls into `work/seo/screaming_frog/` here; log deltas in `CRAWL_COMPARISON.md`.

## Crawl snapshot

| Metric | Value |
| --- | ---: |
| Internal URLs | 126 |
| HTML URLs (2xx) | 19 |
| Internal 404 HTML | 4 |
| Mixed content / HTTP URLs (internal) | 19 URLs (~15% of internal) |
| Missing meta (category hubs) | 3 |
| Missing H1 (many templates) | 12 of 19 HTML (2xx) |

## High-priority fix themes (from audit)

1. **404 HTML** — four dead URLs including `http://hogeyecameras.com/resources` and three HTTPS posts.
2. **Mixed content** — HTTP asset URLs on HTTPS pages (uploads, PDFs).
3. **Category hubs** — missing meta descriptions and H1 parsing gaps.
4. **Buy Now** — thin content, short title, missing H1 in Spider parse.
5. **Images** — missing alt text (5 images flagged).

## Next comparison crawl

Run from this repo via MCP (see `docs/SCREAMING_FROG_MCP.md`):

- **Project name:** `hogeye` (Spider project label)
- **Crawl name:** `YYYY.MM.DD-agt-hogeye` (match export folder)
- **Start URL:** `https://hogeyecameras.com/`

After export, log metrics in `CRAWL_COMPARISON.md` and refresh `TRACKER.csv` statuses.
