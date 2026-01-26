# DataForSEO API Bible (v3)

This doc is a **practical reference** for using DataForSEO’s API v3 inside this repo (TTT clients). It’s structured by DataForSEO “API families”, with consistent notes on **what it is**, **when to use it**, **Live vs Standard**, **cost/rate-limit gotchas**, and **safe starter patterns**.

Primary vendor docs (overview pages):

- SERP API: `https://docs.dataforseo.com/v3/serp/overview/`
- AI Optimization API: `https://docs.dataforseo.com/v3/ai_optimization/overview/`
  - LLM Mentions: `https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/overview/`
  - AI Keyword Data: `https://docs.dataforseo.com/v3/ai_optimization/ai_keyword_data/overview/`
- Keywords Data API: `https://docs.dataforseo.com/v3/keywords_data/overview/`
- Domain Analytics API: `https://docs.dataforseo.com/v3/domain_analytics/overview/`
- Backlinks API: `https://docs.dataforseo.com/v3/backlinks/overview/`
- OnPage API: `https://docs.dataforseo.com/v3/on_page/overview/`
- Content Analysis API: `https://docs.dataforseo.com/v3/content_analysis/overview/`
- Content Generation API: `https://docs.dataforseo.com/v3/content_generation/overview/`
- Merchant API: `https://docs.dataforseo.com/v3/merchant/overview/`
- App Data API: `https://docs.dataforseo.com/v3/app_data/overview/`
- Business Data API: `https://docs.dataforseo.com/v3/business_data/overview/`

---

## How we authenticate (in this repo)

DataForSEO uses **HTTP Basic Auth** with your DataForSEO API credentials (not an API key).

Set in `.env` (git-ignored):

```text
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
DATAFORSEO_LOCATION_CODE=2840
DATAFORSEO_LANGUAGE_CODE=en
```

Notes:

- `DATAFORSEO_LOCATION_CODE` and `DATAFORSEO_LANGUAGE_CODE` strongly affect whether you get non-null metrics.
- Many “Live” endpoints return instantly and are easiest for smoke tests.

---

## Live vs Standard (the core concept)

DataForSEO commonly offers two result-delivery models:

- **Live**: single request, immediate response (highest cost, simplest integration).
- **Standard**: POST a task → poll “Tasks Ready” → GET results (cheaper, more moving parts).

Some API families are **Live-only**:

- Backlinks API (Live-only) – per overview.
- Content Analysis API (Live-only) – per overview.
- Content Generation API (Live-only) – per overview.
- AI Keyword Data API (Live-only) – per overview.
- LLM Mentions API (Live-only) – per overview.

Some are **Standard-only**:

- Merchant API (Standard-only) – per overview.
- App Data API (Standard-only) – per overview.

---

## Cost + rate limits (common guardrails)

High-level defaults (confirm in pricing pages):

- Many endpoints allow up to **2000 API calls/min** (often with “<= 100 tasks per POST” when task-based).
- Several families note **max 30 simultaneous requests** for Live.

Repo guidance:

- Start with **single-keyword / single-domain** smoke tests.
- Only scale up after you confirm location/language settings return meaningful data.

---

## Python “hello world” request pattern

Use this pattern for most DataForSEO endpoints in this repo:

```python
import requests

API_BASE = "https://api.dataforseo.com/v3"
login = "..."      # from env
password = "..."   # from env

endpoint = f"{API_BASE}/keywords_data/google_ads/search_volume/live"
payload = [{
    "location_code": 2840,
    "language_code": "en",
    "keywords": ["example keyword"],
}]

r = requests.post(endpoint, json=payload, auth=(login, password), timeout=60)
r.raise_for_status()
data = r.json()
```

Most v3 endpoints:

- Expect payloads as a **list** of task objects: `[{...}, {...}]`
- Return `{"tasks": [...]}`

---

## SERP API

Source: `https://docs.dataforseo.com/v3/serp/overview/`

### What it is
Retrieve search engine result pages (SERPs) across Google/Bing/YouTube/etc., with location/language/device emulation. Includes optional screenshot + AI Summary endpoints (where available).

### When to use it (TTT blueprint)

- **Rank snapshot** for controlled keyword sets (baseline + monthly).
- **SERP competitor discovery** (what domains show up for your target terms).
- SERP feature analysis (depending on endpoint/function).

### Live vs Standard

- Supports **Live** and **Standard** methods (per overview).

### Common gotchas

- **Location/language/device** materially change results.
- Cost increases with `depth` (per overview).

### Repo usage

- `scripts/seo/dataforseo_benchmark_rank_snapshot.py` uses:
  - `POST /v3/serp/google/organic/live/advanced`
  - with `depth=20`, `device=desktop`, `os=windows`

---

## AI Optimization API

Source: `https://docs.dataforseo.com/v3/ai_optimization/overview/`

### What it is
APIs for AI search optimization: keyword discovery, conversational optimization, and LLM benchmarking.

DataForSEO highlights:

- **LLM Responses API**: generate structured responses from LLMs (ChatGPT/Claude/Gemini/Perplexity).
- **AI Keyword Data API**: search volume estimates reflecting usage in AI tools.
- **LLM Mentions API**: measure brand/keyword/domain mentions in LLMs.

### Live vs Standard

- Mix of Live + Standard depending on sub-API; overview explicitly notes:
  - AI Keyword Data + LLM Mentions are **Live-only**

### Practical use (TTT blueprint)

- Track “AI visibility” signals (mentions, top domains/pages).
- Discover how users phrase queries in conversational interfaces.
- Benchmark how competitors appear in LLM responses (where applicable).

---

## LLM Mentions API (AI Optimization)

Source: `https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/overview/`

### What it is
Mentions counts, quoted links, and aggregated metrics for keywords/domains in LLM outputs.

### Key endpoints (per overview)

- `search/live`
- `aggregated_metrics/live`
- `cross_aggregated_metrics/live`
- `top_domains/live`
- `top_pages/live`

### Live vs Standard

- **Live-only** (per overview).

---

## AI Keyword Data API (AI Optimization)

Source: `https://docs.dataforseo.com/v3/ai_optimization/ai_keyword_data/overview/`

### What it is
Keyword “AI search volume” (usage in AI tools) for target keywords.

### Key endpoint (per overview)

- `keywords_search_volume/live`

### Live vs Standard

- **Live-only** (per overview).

---

## Keywords Data API

Source: `https://docs.dataforseo.com/v3/keywords_data/overview/`

### What it is
Keyword metrics + related keyword discovery for Google Ads and Bing, plus trends/clickstream modules.

### Common use (TTT blueprint)

- Build keyword universe for each client (seed → expand → cluster).
- Get **search volume / CPC / competition** signals (market sizing + prioritization).

### Live vs Standard

- Supports Live and Standard (per overview).

### Important restriction
If a request batch includes a keyword in restricted categories, **the whole batch may return no data** (per overview). Keep batches tight and validate early.

### Repo usage

- `scripts/seo/enrich_feb_2026_clusters_dataforseo.py` calls:
  - `POST /v3/keywords_data/google_ads/search_volume/live`

---

## Domain Analytics API

Source: `https://docs.dataforseo.com/v3/domain_analytics/overview/`

### What it is
Website/domain analysis endpoints for:

- **Technologies**: identify site technology stacks.
- **Whois**: Whois enriched with additional stats.

### Live vs Standard

- Overview indicates the main Domain Analytics sub-APIs are **Live-only**.

### When to use it

- Competitor profiling (CMS/platform, analytics tags, ecommerce stacks, etc.).
- Quick domain vetting during competitor research.

---

## Backlinks API

Source: `https://docs.dataforseo.com/v3/backlinks/overview/`

### What it is
Backlink profile data for domains/subdomains/pages: referring domains, backlink lists, anchors, competitors, intersections, time series, bulk endpoints.

### Live vs Standard

- **Live-only** (per overview), with a “max 30 simultaneous requests” note.

### Key endpoints (per overview)

- `index`
- `summary/live`, `history/live`, `backlinks/live`, `anchors/live`
- `referring_domains/live`, `referring_networks/live`
- `competitors/live`, `domain_intersection/live`, `page_intersection/live`
- Bulk endpoints (ranks/backlinks/spam score/referring domains/new+lost)

### When to use it (TTT blueprint)

- Compare a target site vs competitors’ backlink profile (quality + velocity).
- Identify link gaps via intersection endpoints.
- Track new/lost links over time.

---

## OnPage API

Source: `https://docs.dataforseo.com/v3/on_page/overview/`

### What it is
A crawling engine to audit a site (or page) for SEO/tech issues, duplicates, link graphs, non-indexable pages, redirects, etc.

### How it works (high level)

1) `task_post` to start a crawl (optionally with extra parameters like JS execution, resource loading).
2) Fetch results via endpoints like `summary`, `pages`, `resources`, `duplicate_*`, `links`, etc.

### Live vs Standard
The overview calls out:

- “Instant Pages” and “Page Screenshot” are **Live** (single-call).
- Task-based crawl endpoints are task/poll style (Standard-like).

### Cost gotchas
Extra crawl parameters (`load_resources`, `enable_javascript`, `enable_browser_rendering`, etc.) can add charges (per overview).

---

## Content Analysis API

Source: `https://docs.dataforseo.com/v3/content_analysis/overview/`

### What it is
Brand/keyword citation discovery + sentiment analysis across content sources.

### Live vs Standard

- **Live-only** (per overview).

### When to use it

- Brand monitoring.
- Sentiment/citation baseline for a niche.
- Competitor messaging reconnaissance.

---

## Content Generation API

Source: `https://docs.dataforseo.com/v3/content_generation/overview/`

### What it is
NLP-powered content utilities: generate text, meta tags, subtopics, paraphrase, grammar checks, summaries.

### Live vs Standard

- **Live-only** (per overview).

### How we should use it (TTT)

- Assist with outlines, meta drafting, and rewrite passes.
- Still keep final editorial control (voice/claims/compliance).

---

## Merchant API

Source: `https://docs.dataforseo.com/v3/merchant/overview/`

### What it is
E-commerce competitor/product intelligence from Google Shopping + Amazon: products, sellers, specs, pricing, etc.

### Live vs Standard

- **Standard-only** (per overview) (POST task → GET later).

---

## App Data API

Source: `https://docs.dataforseo.com/v3/app_data/overview/`

### What it is
Data about mobile apps on Google Play + App Store: rankings, reviews, listings, etc.

### Live vs Standard

- **Standard-only** (per overview).

---

## Business Data API

Source: `https://docs.dataforseo.com/v3/business_data/overview/`

### What it is
Public business/review data across:

- Google Business Profile + Google Hotels
- Trustpilot
- Tripadvisor
- Social endpoints (Facebook/Pinterest/Reddit)

### Live vs Standard
Mixed (per overview):

- Social endpoints: Live-only
- Google Hotels: Live + Standard
- Others: Standard

---

## What we already use in this repo today

- **Keywords Data (Google Ads Search Volume, Live)** for enrichment:
  - `scripts/seo/enrich_feb_2026_clusters_dataforseo.py`
- **SERP (Google Organic, Live Advanced)** for rank snapshots:
  - `scripts/seo/dataforseo_benchmark_rank_snapshot.py`

Next likely additions for the 2026 blueprint:

- Backlinks API (gap/link velocity, intersections)
- Domain Analytics (tech stack / whois)
- AI Optimization (LLM mentions + AI keyword volume for “AI search” layer)

