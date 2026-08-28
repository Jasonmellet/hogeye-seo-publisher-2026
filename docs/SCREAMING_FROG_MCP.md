# Screaming Frog MCP — HogEye setup

Connects this repo to the **SEO Spider v24 built-in MCP server** for technical SEO crawls, exports, and fix verification.

Canonical shared setup: Shared Knowledge asset `screaming-frog-mcp` (also via `sharedKnowledge` MCP → `show_asset`).

## Prerequisites

1. **Screaming Frog SEO Spider v24+** installed and licensed.
2. MCP enabled: [Configuration → MCP Server](https://www.screamingfrog.co.uk/seo-spider/user-guide/configuration/#mcp-server).
3. **Allowed directory** includes this repo (or `work/seo/screaming_frog/`) so exports can be written by MCP tools.
4. Cursor workspace MCP config (already in repo):

```json
"sf": {
  "url": "http://127.0.0.1:11435/mcp"
}
```

Server key must be **`sf`** (short name). Hyphenated or long server names break Cursor tool naming (~60 character limit).

Also enable **`sharedKnowledge`** (`http://127.0.0.1:8766/mcp`) for doctrine and technical SEO guardrails.

Reload Cursor after editing MCP settings.

## HogEye crawl defaults

| Setting | Value |
| --- | --- |
| Start URL | `https://hogeyecameras.com/` |
| Spider project label | `hogeye` |
| Crawl name pattern | `YYYY.MM.DD-agt-hogeye` |
| Export folder | `work/seo/screaming_frog/<crawl-id>/` |
| Staging | Out of scope unless auditing canonical leakage |

## Operator checklist (full crawl)

1. Confirm Spider MCP is running (endpoint responds; Cursor shows `sf_*` tools).
2. Preflight: target URL, scope, crawl name, export path.
3. Ask agent or run: crawl `https://hogeyecameras.com/` for project `hogeye`, crawl name `2026-05-20-agt-hogeye` (use today’s date).
4. Wait until crawl **and** connected APIs (PageSpeed, etc.) are idle before bulk export.
5. Export `crawl_overview.csv` and `issues_overview_report.csv` minimum.
6. Update `workspace/technical_seo/CRAWL_COMPARISON.md` and triage `TRACKER.csv`.

## Periodic comparison crawls

After each fix batch:

1. Run a **full** crawl (monthly or milestone), **or** a **verification** URL-list crawl for the affected URLs only.
2. Compare headline counts to the previous row in `CRAWL_COMPARISON.md`.
3. Close or update `TRACKER.csv` rows only with `evidence_after` from the new crawl or rendered HTML check.

## Example Cursor prompts

- “Crawl `https://hogeyecameras.com/` for project `hogeye`, crawl name `2026-05-20-agt-hogeye`, and export overview + issues CSVs to `work/seo/screaming_frog/`.”
- “Compare the latest crawl to baseline `2026.04.09.05.15.26` and summarize deltas for 404s and mixed content.”
- “What is crawl progress for the loaded hogeye crawl?”
- “Run a verification crawl on these URLs only: [list] — confirm 404 and mixed content fixes.”

## Intake guardrails

- Raw exports are **read-only evidence** — do not edit CSVs in place; add a new dated folder per crawl.
- Do **not** commit bulk crawl dumps (gitignored under `work/seo/screaming_frog/`).
- Normalize findings in `workspace/technical_seo/TRACKER.csv` before implementing fixes.
- Crawler output does not approve WordPress publishes or live template changes without human review where `hitl_required` is yes.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| No `sf_*` tools in Cursor | Enable `sf` in Settings → MCP; reload window; confirm Spider MCP is on |
| Tools fail silently | Rename server to `sf` only in `.cursor/mcp.json` |
| Export write fails | Add repo path to Spider MCP allowed directories |
| Endpoint unreachable | Open SEO Spider; enable MCP server |

## Related docs

- [`workspace/technical_seo/README.md`](../workspace/technical_seo/README.md) — tracker + comparison workflow
- [`workspace/RUNBOOK.md`](../workspace/RUNBOOK.md) — execution checklist
- **Advanced SEO Analysis** repo: `docs/mcp-screaming-frog.md` (same MCP endpoint pattern)
- April 2026 baseline: [`workspace/technical_seo/BASELINE.md`](../workspace/technical_seo/BASELINE.md)
