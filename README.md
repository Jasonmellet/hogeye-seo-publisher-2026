# SEO Content Publisher Template

Two tightly-connected systems (per client repo):

- **WordPress Publishing Engine**: publish/update pages + posts to WordPress via REST API, draft-first, with validation gates.
- **SEO Planning Engine**: build a data-driven monthly plan in Google Sheets (Semrush normalization, sitemap inventory, DataForSEO enrichment, execution checklists).

## Project Overview

This repo is a GitHub template intended to be the source-of-truth + automation toolkit for each client:

- **Publishing**: JSON “source of truth” → transforms/validators → WordPress drafts/updates.
- **Planning**: Semrush exports + DataForSEO → clustered plan → briefs → checklists → measurement tabs in Sheets.

## Quick Start

### WordPress publisher (local, per client)

New client? Start with `CLIENT_SETUP.md`.

1. Create a local virtualenv (recommended on macOS/Homebrew Python):

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

1. Configure environment:

```bash
cp env.example .env
# Edit .env with your WordPress credentials
```

1. Test connection:

```bash
./.venv/bin/python test_connection.py
```

1. Publish content (canonical pipeline; draft-first by default):

```bash
# Publish a single item (recommended)
./.venv/bin/python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts

# Or publish a batch directory
./.venv/bin/python publish_batch.py /absolute/path/to/content/posts --type posts
```

### SEO planning engine (Sheets)

We maintain planning artifacts under `work/seo/` and push them to your Google Sheet via scripts in `scripts/seo/`.

- **Key script**: `scripts/seo/push_seo_csvs_to_sheet.py`
- **Example execution tab**: `Feb_2026_execution_checklists` (generated from `Feb_2026_plan_final` + `Feb_2026_briefs`)
- **Note**: This repo assumes a paid DataForSEO plan is available (Keywords/SERP + Backlinks; AI Optimization optional). Keep credentials in `.env` (git-ignored).

## Project Structure

```text
repo_root/
├── README.md                 # This file
├── DOCS.md                  # Documentation index (see docs/)
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables template
├── .env                    # Your credentials (git-ignored)
├── config.py               # Configuration handler
├── publish_content_item.py # Canonical: publish/update ONE item
├── publish_batch.py        # Canonical: publish/update a batch
├── resolve_internal_links.py# Optional: resolve {{link:...}} placeholders across existing WP content
├── content/
│   ├── pages/             # Landing pages (JSON/Markdown)
│   ├── posts/             # Blog posts (JSON/Markdown)
│   └── images/            # Image files
├── modules/
│   ├── auth.py            # WordPress authentication
│   ├── publish_pipeline.py # Canonical pipeline (draft-first)
│   ├── images.py           # Image uploader
│   ├── metadata.py         # Yoast meta helpers
│   └── links.py            # Internal linking
├── scripts/
│   ├── seo/                # SEO planning scripts (Semrush/DataForSEO/Sheets)
│   └── legacy/             # Deprecated one-offs (avoid for monthly publishing)
└── logs/                   # Execution logs (git-ignored)

```

## Status Tracking

- **Publisher**
  - [x] WordPress auth + permissions verified (`test_connection.py`)
  - [x] Draft-first canonical pipeline in place
  - [x] Homepage safety guardrails (protect countdown markers)
  - [ ] Feb Wave 1 + Wave 2 execution (draft → review → publish)
- **SEO planning**
  - [x] Sitemap inventory
  - [x] Semrush OTI normalization + non-brand filtering + cannibalization
  - [x] Feb 2026 plan: constraints → clusters → final 10 → briefs → checklists → measurement scaffolding

## Documentation

See `DOCS.md` for the full documentation index.

## Git workflow

Recommended branches:

- `main`: stable
- `develop`: active development

## Support

For issues or questions, refer to the documentation files above.
