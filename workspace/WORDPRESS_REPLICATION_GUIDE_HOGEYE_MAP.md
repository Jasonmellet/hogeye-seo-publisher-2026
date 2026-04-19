# Mapping: generic replication guide → this HogEye repo

The [`WORDPRESS_PUBLISHING_REPLICATION_GUIDE.md`](../docs/WORDPRESS_PUBLISHING_REPLICATION_GUIDE.md) describes **patterns** (Librarian layer, SEO gates, draft WordPress sync) using illustrative paths from a markdown-first “Theo” template.

**This repository** implements the same *ideas* under `workspace/` and the Python publisher under `scripts/publisher/`.

| Concept in replication guide | HogEye location |
| --- | --- |
| Librarian (doctrine alignment) | [`content_system/workflows/librarian_workflow.md`](content_system/workflows/librarian_workflow.md); commands: `npm run librarian:audit`, `npm run librarian:apply` |
| SEO / editorial governance | [`content_pipeline/WORKFLOW.md`](content_pipeline/WORKFLOW.md), [`content_pipeline/LLM_OPERATOR_INSTRUCTIONS.md`](content_pipeline/LLM_OPERATOR_INSTRUCTIONS.md), monthly `queue/`, `qa/` |
| Evidence / truth rules | [`content_system/config/evidence_and_truth.md`](content_system/config/evidence_and_truth.md); brand: [`brand_truth/`](brand_truth/) |
| Ingestion (video/text) | [`content_pipeline/sources/`](content_pipeline/sources/); npm: `transcribe`, `process-transcript`, `ingest-source` |
| npm WordPress scripts (`wp:create-draft`) | **Not shipped here.** Draft publishing uses **Python**: [`scripts/publisher/publish_content_item.py`](../../../../scripts/publisher/publish_content_item.py) with JSON produced by [`scripts/seo/hogeye_draft_md_to_post_json.py`](../../../../scripts/seo/hogeye_draft_md_to_post_json.py) |
| Sitemap allowlist | [`ops/SITEMAP_AND_LINKS.md`](ops/SITEMAP_AND_LINKS.md); [`scripts/seo/ttt_benchmark_sitemap_inventory.py`](../../../../scripts/seo/ttt_benchmark_sitemap_inventory.py) |
| Phase 2 WP bridge | [`content_system/workflows/phase_two_wordpress_bridge.md`](content_system/workflows/phase_two_wordpress_bridge.md) |

Optional env: `HOGEYE_WORKSPACE_REL` (see [`env.example`](../../../../env.example)) if the HogEye tree is moved; default is `hogeye`.
