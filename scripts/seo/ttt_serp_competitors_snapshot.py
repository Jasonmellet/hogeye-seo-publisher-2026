#!/usr/bin/env python3
"""
Pull a small SERP snapshot for a keyword list and summarize competitor domains.

Input:
  - CSV with a 'keyword' column (defaults to work/seo/plan/{client}_keywords_for_site.csv)

Output:
  - work/seo/plan/{client}_serp_competitor_domains.csv

This is designed to work before GSC is available: it identifies the *real* SERP
competitors for the site's topic space.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


def _clean_client_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


def _read_keywords(path: str, col: str) -> List[str]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        out: List[str] = []
        for row in r:
            kw = (row.get(col) or "").strip()
            if kw:
                out.append(kw)
        # de-dupe preserving order
        seen = set()
        ded = []
        for k in out:
            kl = k.lower()
            if kl in seen:
                continue
            seen.add(kl)
            ded.append(k)
        return ded


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _infer_domain_from_env() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    return (urlparse(wp_site).hostname or "").strip().lower()


def _dfs_serp_google_organic_live(
    *,
    login: str,
    password: str,
    keyword: str,
    location_code: int,
    language_code: str,
    depth: int,
) -> List[dict]:
    url = f"{API_BASE}/serp/google/organic/live/advanced"
    body = [
        {
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": "desktop",
            "os": "windows",
            "depth": depth,
        }
    ]
    r = requests.post(url, json=body, auth=(login, password), timeout=90)
    r.raise_for_status()
    data = r.json()
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    res0 = tasks[0].get("result") or []
    if not res0:
        return []
    items = res0[0].get("items") or []
    organic = [it for it in items if (it.get("type") or "").lower() in ["organic", "google_organic", "organic_extended"]]
    return organic or items


def main() -> int:
    ap = argparse.ArgumentParser(description="Build SERP competitor domain snapshot via DataForSEO SERP API.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--client-key", default="client", help="Prefix for default input/output file paths")
    ap.add_argument("--keywords-csv", default="", help="CSV with keywords (overrides --client-key default)")
    ap.add_argument("--keywords-col", default="keyword", help="Column name containing keywords")
    ap.add_argument("--max-keywords", type=int, default=25, help="How many keywords to sample (default 25)")
    ap.add_argument("--depth", type=int, default=10, help="SERP depth to consider (default 10)")
    ap.add_argument("--target-domain", default="", help="Target domain (defaults to WP_SITE_URL host)")
    ap.add_argument("--output", default="", help="Output CSV path (overrides --client-key default)")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD (set in .env).")

    client_key = _clean_client_key(args.client_key)
    if not args.keywords_csv:
        args.keywords_csv = f"work/seo/plan/{client_key}_keywords_for_site.csv"
    if not args.output:
        args.output = f"work/seo/plan/{client_key}_serp_competitor_domains.csv"

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en") or "en").strip()

    target_domain = (args.target_domain or _infer_domain_from_env()).strip().lower().lstrip(".")
    if not target_domain:
        raise SystemExit("Missing --target-domain and could not infer from WP_SITE_URL.")

    kws = _read_keywords(args.keywords_csv, args.keywords_col)[: max(1, int(args.max_keywords))]
    fetched_at = datetime.now(timezone.utc).isoformat()

    domain_counts: Counter[str] = Counter()
    domain_example_kw: Dict[str, str] = {}
    domain_example_url: Dict[str, str] = {}

    for kw in kws:
        items = _dfs_serp_google_organic_live(
            login=login,
            password=password,
            keyword=kw,
            location_code=location_code,
            language_code=language_code,
            depth=max(1, int(args.depth)),
        )
        for it in items[: max(1, int(args.depth))]:
            dom = (it.get("domain") or "").strip().lower()
            url = (it.get("url") or "").strip()
            if not dom:
                continue
            domain_counts[dom] += 1
            domain_example_kw.setdefault(dom, kw)
            if url:
                domain_example_url.setdefault(dom, url)

    rows: List[Dict[str, object]] = []
    for dom, cnt in domain_counts.most_common():
        rows.append(
            {
                "domain": dom,
                "appearances": cnt,
                "example_keyword": domain_example_kw.get(dom, ""),
                "example_url": domain_example_url.get(dom, ""),
                "is_target_domain": "yes" if (dom == target_domain or dom.endswith("." + target_domain)) else "no",
                "location_code": location_code,
                "language_code": language_code,
                "fetched_at": fetched_at,
            }
        )

    _write_csv(
        args.output,
        ["domain", "appearances", "example_keyword", "example_url", "is_target_domain", "location_code", "language_code", "fetched_at"],
        rows,
    )
    print("OK")
    print("wrote:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

