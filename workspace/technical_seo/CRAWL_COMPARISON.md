# HogEye Screaming Frog — crawl comparison log

Record **headline metrics** after each crawl so we can see whether fixes are working. Raw exports stay in `work/seo/screaming_frog/<crawl-id>/`.

## How to use

1. After each crawl completes, export at least `crawl_overview.csv` and `issues_overview_report.csv`.
2. Fill one row below (copy metrics from `crawl_overview.csv` / issues report).
3. Note which tracker issue IDs were targeted since the previous crawl.
4. Prefer **focused URL-list crawls** for single-issue verification; use **full site crawls** for periodic checkpoints (e.g. monthly or after a fix batch).

## Comparison table

| crawl_id | date | type | internal_urls | html_2xx | internal_404 | mixed_content_urls | http_urls | missing_meta_html | missing_h1_html | notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026.04.09.05.15.26 | 2026-04-09 | baseline (audit repo) | 126 | 19 | 4 | 19 | 19 | 3 | 12 | See `BASELINE.md`; evidence in Advanced SEO Analysis |
| 2026.05.21.07.33.25-agt-hogeye | 2026-05-21 | full | 168 | 34 | 6 | 34 | 19 | 8 | 17 | MCP crawl `2026-05-21-agt-hogeye`; exports in `work/seo/screaming_frog/2026.05.21.07.33.25-agt-hogeye/`; client audit `HOGEYE_TECHNICAL_SEO_AUDIT_2026-05-21.md` |
| 2026.06.22.agt-cursor | 2026-06-22 | full (audit repo MCP) | 167 | 34 | 6 | 34 | 19 | 8 | 17 | Migrated from Advanced SEO Analysis; exports in `work/seo/screaming_frog/2026.06.22.agt-cursor/`; findings in `content_pipeline/research/sprint_20260622_audit/findings/technical-findings.md` |

### Type values

- `baseline` — initial reference crawl
- `full` — production site crawl after fix batch
- `verification` — URL list or narrow scope to confirm one issue class

## Issue-class deltas (optional detail)

When comparing two crawls, paste issue counts from `issues_overview_report.csv` for classes you are actively fixing:

| issue_class | baseline (2026-04-09) | latest crawl | delta |
| --- | ---: | ---: | ---: |
| Response Codes: Internal Client Error (4xx) | 4 | 6 | +2 |
| Security: Mixed Content | 19 | 34 | +15 |
| Security: HTTP URLs | 19 | 19 | 0 |
| Page Titles: Below 30 Characters | 4 | 5 | +1 |
| Meta Description: Missing | 3 | 8 | +5 |
| H1: Missing | 12 | 17 | +5 |
| Images: Missing Alt Text | 5 | 4 | −1 |

Update **latest crawl** after each new export.
