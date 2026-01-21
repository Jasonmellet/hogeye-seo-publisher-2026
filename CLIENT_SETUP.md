# Client Setup (Template Repo)

This repo is meant to be used as a **GitHub Template repository** so each client gets a **separate repo** with strict isolation.

## Create a new client project (GitHub)
1. In GitHub, open this repo → click **Use this template** → create a new private repo (example: `clientname-seo-publisher`).
2. Clone the new repo locally.

Recommended client repos:
- `camp-lakota-seo-publisher`
- `boar-blanket-seo-publisher`
- `hog-eye-cameras-seo-publisher`

## Local setup (per client)
1. Create venv + install deps:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

2. Create `.env` (credentials live here; never commit):

```bash
cp env.example .env
```

3. Create client config (safe to commit; used for guardrails):

```bash
cp client.config.example.json client.config.json
```

4. Generate **fresh WordPress Application Password** for this client:
- WordPress Admin → Users → Your Profile → Application Passwords
- Name suggestion: `SEO Content Publisher`

5. Validate connection before publishing:

```bash
./.venv/bin/python test_connection.py
```

## Local-only bootstrap (optional)

If you want to scaffold a new client folder locally (without GitHub) you can use:

```bash
chmod +x scripts/bootstrap_client_repo.sh
./scripts/bootstrap_client_repo.sh /abs/path/to/new-client-repo "Client Name" "https://client-site.com"
```

## Canonical monthly publishing commands
- Publish ONE item:

```bash
./.venv/bin/python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts
```

- Publish a batch:

```bash
./.venv/bin/python publish_batch.py /absolute/path/to/content/posts --type posts
```

## SEO planning (optional)

If you’re using the SEO scripts under `scripts/seo/`, you typically set:

- `SEO_SPREADSHEET_ID`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GSC_SITE_URL`
- `GA4_PROPERTY_ID` (optional)
- `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` (optional)

Then run (example):

```bash
./.venv/bin/python scripts/seo/run_benchmark.py --project-root "$(pwd)" --site-url "$GSC_SITE_URL" --spreadsheet-id "$SEO_SPREADSHEET_ID"
```

## Required reading (do this once)
- `docs/QUICK_START.md`
- `docs/SECURITY.md`
- `docs/MONTHLY_PUBLISHING_WORKFLOW.md`

