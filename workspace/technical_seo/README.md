# HogEye technical SEO (Screaming Frog)

Agent-assisted technical fixes for **https://hogeyecameras.com/** using Screaming Frog MCP plus a normalized tracker and periodic comparison crawls.

## Quick start

1. Open **SEO Spider v24+** and enable **Configuration → MCP Server** ([user guide](https://www.screamingfrog.co.uk/seo-spider/user-guide/configuration/#mcp-server)).
2. Allow this repo path in MCP allowed directories (see `work/seo/screaming_frog/README.md`).
3. In Cursor: enable MCP servers **`sf`** and **`sharedKnowledge`** for this workspace; reload the window.
4. Run a baseline comparison crawl (see `CRAWL_COMPARISON.md`).
5. Triage and fix from `TRACKER.csv`; verify with focused or full re-crawls.

Setup details: [`docs/SCREAMING_FROG_MCP.md`](../../docs/SCREAMING_FROG_MCP.md)

## Files

| File | Role |
| --- | --- |
| `TRACKER.csv` | Normalized remediation queue (versioned) |
| `CRAWL_COMPARISON.md` | Periodic crawl snapshots — prove fixes are taking effect |
| `BASELINE.md` | April 2026 audit summary + evidence pointers |
| `HOGEYE_TECHNICAL_SEO_AUDIT_2026-05-21.md` | Client-facing technical audit (May 2026 crawl) — forward to Phil |

## Crawl scope (production)

- **Include:** `https://hogeyecameras.com/`
- **Exclude:** `https://staging.hogeyecameras.com/` unless explicitly auditing canonical/indexation leakage

## Workflow (shared knowledge)

1. **Preflight** — confirm target, scope, and export destination before `sf_crawl`.
2. **Evidence** — save raw exports under `work/seo/screaming_frog/<dated-folder>/` (immutable for that crawl ID).
3. **Normalize** — add or update rows in `TRACKER.csv` (do not fix directly from CSV exports).
4. **Ownership** — classify: content, metadata, media, template, CMS/plugin, redirect, platform, external, false_positive.
5. **Implement** — repo-owned fixes only; hand off platform/CMS items explicitly.
6. **Verify** — re-crawl or URL-list check; log result in `CRAWL_COMPARISON.md` and close tracker rows with `evidence_after`.

Shared assets (via `sharedKnowledge` MCP): `screaming-frog-mcp`, `screaming-frog-mcp-intake-guardrails`, `technical-seo-crawl-fix`, `technical-seo-tracker`.

## Related audit repo

Historical crawl + `technical-findings.md` live in **Advanced SEO Analysis** (`clients/hogeye/`). This Hogeye repo owns **fixes and verification** going forward; copy new exports here rather than editing audit inputs in place.
