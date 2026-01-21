#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a new client repo folder from this template (local-only).
#
# Usage:
#   ./scripts/bootstrap_client_repo.sh /abs/path/to/new-client-repo "Client Name" "https://client-site.com"
#
# Notes:
# - This does NOT create a GitHub repo. It only scaffolds a local folder so you can init git or copy into a new repo.
# - Secrets are not created; you'll still create `.env` locally.

dest="${1:-}"
client_name="${2:-}"
wp_site_url="${3:-}"

if [[ -z "${dest}" || -z "${client_name}" || -z "${wp_site_url}" ]]; then
  echo "Usage: $0 /abs/path/to/new-client-repo \"Client Name\" \"https://client-site.com\""
  exit 2
fi

if [[ "${dest}" != /* ]]; then
  echo "Error: destination must be an absolute path (got: ${dest})"
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "${dest}"

echo "Copying template -> ${dest}"
rsync -a --delete \
  --exclude ".git/" \
  --exclude ".venv/" \
  --exclude "venv/" \
  --exclude ".env" \
  --exclude "logs/" \
  --exclude "work/" \
  --exclude "archive/" \
  --exclude "backups/" \
  "${root}/" "${dest}/"

cd "${dest}"

if [[ ! -f "client.config.example.json" ]]; then
  echo "Error: missing client.config.example.json in destination"
  exit 2
fi

cp -n env.example .env
cp -n client.config.example.json client.config.json

# Derive host safely
wp_host="$(python3 - <<'PY'
import sys
from urllib.parse import urlparse
u = sys.argv[1].strip()
print((urlparse(u).hostname or "").strip())
PY
"${wp_site_url}")"
if [[ -z "${wp_host}" ]]; then
  echo "Error: could not parse host from WP site URL: ${wp_site_url}"
  exit 2
fi

# Best-effort fill client.config.json without requiring jq/python parsing.
# We keep this minimal: user can edit as needed.
tmp="$(mktemp)"
sed \
  -e "s/\"clientName\": \"Client Name Here\"/\"clientName\": \"${client_name//\"/\\\"}\"/" \
  -e "s#\"expectedWpSiteUrl\": \"https://your-site.com\"#\"expectedWpSiteUrl\": \"${wp_site_url%/}\"#" \
  -e "s#\"expectedWpSiteHost\": \"your-site.com\"#\"expectedWpSiteHost\": \"${wp_host}\"#" \
  client.config.json > "${tmp}"
mv "${tmp}" client.config.json

echo ""
echo "Done."
echo "Next:"
echo "- Edit .env with WP creds (WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD)"
echo "- Review client.config.json and fix expectedWpSiteHost if needed"
echo "- Run: python3 test_connection.py"

