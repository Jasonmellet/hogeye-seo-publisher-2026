# Screaming Frog crawl exports (local only)

Raw MCP and Spider exports live here. **Do not commit** bulk CSVs or `.dbseospider` files — they are gitignored.

## Folder naming

```
work/seo/screaming_frog/<YYYY.MM.DD.HH.MM.SS>-agt-hogeye/
```

Example: `2026.05.20.14.30.00-agt-hogeye/`

## Minimum exports per crawl

| File | Purpose |
| --- | --- |
| `crawl_overview.csv` | Snapshot metrics for comparison |
| `issues_overview_report.csv` | Issue counts by class |
| `crawl_export.dbseospider` | Native Spider archive (optional) |

Add tab-specific CSVs only when fixing that issue class (titles, meta, H1, mixed content, 404s, etc.).

## Allowed directory (Screaming Frog MCP)

In SEO Spider **Configuration → MCP Server**, allow this repo (or parent) so `sf_*` write tools can save exports here. After changing allowed paths, reload Cursor.

## Comparison log

Record crawl IDs and headline deltas in `workspace/technical_seo/CRAWL_COMPARISON.md`.

## Baseline reference

April 2026 audit crawl (read-only reference, Advanced SEO Analysis repo):

`Advanced SEO Analysis/clients/hogeye/inputs/screaming_frog/2026.04.09.05.15.26/`

Summarized findings: `workspace/technical_seo/BASELINE.md`
