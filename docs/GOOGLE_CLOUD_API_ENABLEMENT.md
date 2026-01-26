# Google Cloud API Enablement (required for GSC/GA4/Sheets)

If you see errors like **“API has not been used in project … before or it is disabled”**, it means the Google Cloud project behind your service account needs APIs enabled.

## Enable these APIs (one-time per Google Cloud project)

In the Google Cloud Console, enable:

- **Google Search Console API** (required for `scripts/seo/gsc_benchmark_pull.py`)
- **Google Analytics Data API** (required for `scripts/seo/ga4_benchmark_pull.py`)
- **Google Sheets API** (required for pushing benchmark tabs to the planning sheet)
- **Google Drive API** (recommended; helps with Sheets/Docs access patterns)

After enabling, wait **2–10 minutes** for permissions to propagate.

## Confirm `.env` points at your service account JSON

Set (example):

```text
GOOGLE_APPLICATION_CREDENTIALS="/abs/path/to/SEO-Publisher-Repo/secrets/ttt-google-service-account.json"
```

## Re-run benchmarks

Once APIs are enabled and the service account has been added to the client’s GA4 + GSC:

```bash
./.venv/bin/python scripts/seo/run_benchmark.py \
  --project-root "$(pwd)" \
  --site-url "sc-domain:example.com" \
  --ga4-property-id "123456789" \
  --service-account-json "secrets/ttt-google-service-account.json"
```

If you want to proceed even when one source is still pending, use:

```bash
./.venv/bin/python scripts/seo/run_benchmark.py \
  --project-root "$(pwd)" \
  --site-url "sc-domain:example.com" \
  --ga4-property-id "123456789" \
  --service-account-json "secrets/ttt-google-service-account.json" \
  --allow-partial
```
