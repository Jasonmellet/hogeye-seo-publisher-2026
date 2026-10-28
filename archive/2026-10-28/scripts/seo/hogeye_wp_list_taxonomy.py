#!/usr/bin/env python3
"""
List WordPress category and tag names (and ids) via REST API — use for SEO taxonomy alignment.

Requires .env: WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD (Application Password).

Usage:
  ./.venv/bin/python scripts/seo/hogeye_wp_list_taxonomy.py
  ./.venv/bin/python scripts/seo/hogeye_wp_list_taxonomy.py --json
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def _fetch_all(
    session: requests.Session,
    base: str,
    kind: str,
    *,
    per_page: int = 100,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = session.get(
            f"{base}/wp/v2/{kind}",
            params={"per_page": per_page, "page": page, "context": "view"},
            timeout=45,
        )
        if r.status_code != 200:
            print(f"HTTP {r.status_code} for /wp/v2/{kind}", file=sys.stderr)
            print((r.text or "")[:800], file=sys.stderr)
            raise SystemExit(2)
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="List WP categories and tags (REST)")
    ap.add_argument("--project-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Print JSON instead of tables")
    args = ap.parse_args()

    root = args.project_root.resolve()
    load_dotenv(root / ".env", override=False)
    site = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    user = (os.environ.get("WP_USERNAME") or "").strip()
    password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not site or not user or not password:
        print("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env", file=sys.stderr)
        return 2

    session = requests.Session()
    session.auth = HTTPBasicAuth(user, password)
    session.headers.update(
        {
            "User-Agent": "HogEye-WP-Taxonomy-List/1.0",
            "Accept": "application/json",
        }
    )
    api = f"{site}/wp-json"

    cats = _fetch_all(session, api, "categories")
    tags = _fetch_all(session, api, "tags")

    if args.json:
        def _n(x: Any) -> str:
            return html.unescape(str(x or ""))

        print(
            json.dumps(
                {
                    "site": site,
                    "categories": [
                        {"id": c.get("id"), "name": _n(c.get("name")), "slug": c.get("slug")} for c in cats
                    ],
                    "tags": [{"id": t.get("id"), "name": _n(t.get("name")), "slug": t.get("slug")} for t in tags],
                },
                indent=2,
            )
        )
        return 0

    print(f"Site: {site}\n")
    print("## Categories (use exact `name` in - categories: …)\n")
    for c in sorted(cats, key=lambda x: html.unescape(x.get("name") or "").lower()):
        nm = html.unescape(c.get("name") or "")
        print(f"  {c.get('id', ''):>6}  {nm}")
    print(f"\n  Total: {len(cats)}\n")
    print("## Tags\n")
    for t in sorted(tags, key=lambda x: html.unescape(x.get("name") or "").lower()):
        nm = html.unescape(t.get("name") or "")
        print(f"  {t.get('id', ''):>6}  {nm}")
    print(f"\n  Total: {len(tags)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
