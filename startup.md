# Startup (credential intake + first-run checklist)

This doc is optimized for **Jason’s workflow** and for **Cursor AI agents** assisting in this repo.

## Operator preference (Jason)

- Jason does **not** want to run terminal commands manually.
- If you are an AI agent: **ask for confirmation**, then run steps yourself.
- Default to **draft-first**. Do not publish live unless Jason explicitly confirms.

## Before we can start: what you (Jason) must bring

Do **not** paste secrets into chat. Put them in **`.env`** (local-only) and/or a local **service account JSON** file referenced by `.env`.

### Required (WordPress publishing)

- **WP_SITE_URL**: exact canonical site URL (no trailing slash)  
  Example: `https://www.example.com`
- **WP_USERNAME**: WP admin/editor username for REST API writes
- **WP_APP_PASSWORD**: WordPress *Application Password* (with spaces)
- **client.config.json** values (commit-safe, but must match the target site):
  - `clientName`
  - `expectedWpSiteUrl`
  - `expectedWpSiteHost`
  - (optional) `expectedWpSiteName`

### Optional (SEO planning / measurement)

If you want to use `scripts/seo/*`, you’ll need:

- **SEO_SPREADSHEET_ID**: Google Sheet ID for the planning sheet
- **GOOGLE_APPLICATION_CREDENTIALS**: absolute path to a Google service account JSON key file
- **GSC_SITE_URL**: Search Console property, recommended domain property  
  Example: `sc-domain:example.com`
- **GA4_PROPERTY_ID** (optional): numeric GA4 property id
- **DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD** (optional): DataForSEO API creds
- (optional) **BRAND_TERMS**: comma-separated brand tokens to exclude in query lists

## After you provide those, the agent should do this (in order)

1) **Verify config guardrails**
- Confirm `.env` `WP_SITE_URL` equals `client.config.json` `expectedWpSiteUrl`
- Confirm host matches `expectedWpSiteHost`

2) **Install dependencies** (one-time per repo)
- Create `.venv` and install `requirements.txt`

3) **Connection test** (read-only)
- Run `test_connection.py` and confirm REST API + auth works

4) **Dry run rehearsal**
- Set `DRY_RUN=true`
- Run `publish_content_item.py` on *one* content JSON file (no WordPress writes)

5) **Draft-first publish**
- Set `DRY_RUN=false`
- Publish/update as **draft**
- Review in WordPress admin (desktop + mobile)

6) **Only then: publish live**
- Explicit Jason confirmation required

## Quick “agent prompts” (use these questions)

When starting a fresh client repo, ask Jason:

1) “What is the exact WordPress site URL we’re publishing to (including `www` if applicable)?”
2) “Do you already have a WordPress Application Password for this site, or should we generate one?”
3) “Do we need SEO scripts for this client now? If yes, what is the planning Sheet ID?”
4) “Do we have a Google service account JSON that has access to the Sheet + GSC + GA4? Where is it stored locally?”
5) “What is the GSC property string (`sc-domain:...` or URL-prefix)?”
6) “What is the GA4 numeric property id (if we want GA4 pulls)?”
7) “Do we have DataForSEO credentials (if we want SERP snapshots/enrichment)?”

## Related docs

- `starter.md`: full operational overview of the workflow
- `CLIENT_SETUP.md`: per-client setup checklist (template workflow)

