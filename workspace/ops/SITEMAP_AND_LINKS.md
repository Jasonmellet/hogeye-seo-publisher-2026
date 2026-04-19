# Sitemap inventory and internal linking (HogEye)

## Refresh the URL allowlist

From the repo root (`.env` must set `WP_SITE_URL` for the HogEye site):

```bash
./.venv/bin/python scripts/seo/ttt_benchmark_sitemap_inventory.py \
  --project-root "$(pwd)" \
  --output-dir "work/seo/benchmark/hogeye_sitemap" \
  --max-urls 5000
```

Output: `work/seo/benchmark/hogeye_sitemap/Benchmark_Sitemap_Inventory.csv` with a `url` column.

Use this CSV as the **single source of allowed internal link targets** when suggesting or validating links (no guessed URLs).

## Internal link map + “SEO agent” analysis (site as it exists today)

Crawl **published** posts/pages via WordPress REST, extract same-site `<a href>` edges, compare to `PROJECT_CONFIG.json` `internal_links.targets` (HogEye: **buy now**, **resources**, **blog** — not login/account pages), then optionally run **OpenAI** on an allowlist-only summary (gaps + recommendations + 30-day plan).

```bash
./.venv/bin/python scripts/seo/hogeye_internal_link_deep_dive.py \
  --project-root "$(pwd)" \
  --output-dir workspace/ops/internal_link_deep_dive/latest

./.venv/bin/python scripts/seo/hogeye_internal_link_deep_dive.py \
  --project-root "$(pwd)" \
  --output-dir workspace/ops/internal_link_deep_dive/latest \
  --openai-analysis
```

Outputs: `internal_link_graph.json`, `internal_link_edges.csv`, `INTERNAL_LINK_MAP_REPORT.md`, and with `--openai-analysis` → `SEO_INTERNAL_LINK_ANALYSIS.md`. Requires `OPENAI_API_KEY` for the analysis step; model defaults to **`gpt-5.4`** unless `OPENAI_MODEL` is set.

URLs are **normalized** to one canonical form: scheme + host from `WP_SITE_URL`, **www** and non-www unified, trailing slashes stripped (except `/`), `#fragments` dropped, path segments lowercased by default (`--preserve-path-case` to keep original casing).

## Publish-time linking (Python pipeline)

When publishing JSON posts, `{{link:slug|anchor}}` placeholders resolve via `client.config.json` `linkAliases` and the live WordPress slug map. Keep high-traffic HogEye URLs in `linkAliases` so slugs stay stable.

## Optional: OpenAI link hints (allowlist-only)

After you have an inventory CSV, you can get **non-mutating** suggestions:

```bash
./.venv/bin/python scripts/seo/hogeye_allowlisted_link_hints.py \
  --inventory work/seo/benchmark/hogeye_sitemap/Benchmark_Sitemap_Inventory.csv \
  --article-md workspace/content_pipeline/monthly/2026-04/drafts/apr26_01_draft.md
```

Review suggestions manually; add approved links as `{{link:...}}` in HTML/JSON or in markdown before running the draft → JSON bridge.

Requires `OPENAI_API_KEY` in `.env`. Chat model defaults to **`gpt-5.4-mini`** unless you set `OPENAI_MODEL` or `OPENAI_NOTES_MODEL`.
