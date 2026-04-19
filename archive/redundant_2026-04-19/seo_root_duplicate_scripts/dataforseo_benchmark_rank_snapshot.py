#!/usr/bin/env python3
"""
Fetch a rank snapshot for a controlled keyword set using DataForSEO SERP API.

Outputs (CSV):
  - Benchmark_DataForSEO_RankSnapshot.csv

Notes:
  - Uses DataForSEO login/password from .env or env vars.
  - Finds the first ranking for your target domain in organic results.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


API_BASE = "https://api.dataforseo.com/v3"


def read_keywords_from_csv(path: str, col: str) -> List[str]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        out: List[str] = []
        for row in r:
            kw = (row.get(col) or "").strip()
            if kw:
                out.append(kw)
        return out


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def dedupe(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in seq:
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def chunks(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def parse_serp_find_domain(result_items: List[dict], target_domain: str) -> Tuple[Optional[int], Optional[str], str]:
    """
    Return (best_position, best_url, top_domains_csv)
    """
    td = target_domain.lower().lstrip(".")
    best_pos: Optional[int] = None
    best_url: Optional[str] = None
    top_domains: List[str] = []

    for it in result_items[:20]:
        dom = (it.get("domain") or "").lower()
        url = it.get("url") or ""
        if dom:
            top_domains.append(dom)
        # DataForSEO gives rank_group / rank_absolute; prefer rank_group (organic block rank)
        pos = it.get("rank_group") or it.get("rank_absolute")
        try:
            pos_i = int(pos)
        except Exception:
            pos_i = None

        if dom and (td in dom or dom.endswith(td)):
            if pos_i is not None and (best_pos is None or pos_i < best_pos):
                best_pos = pos_i
                best_url = url or best_url

    # De-dupe domains preserving order
    seen = set()
    uniq = []
    for d in top_domains:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return best_pos, best_url, ", ".join(uniq[:10])


def dfs_serp_google_organic_live(
    *,
    login: str,
    password: str,
    keyword: str,
    location_code: int,
    language_code: str,
) -> List[dict]:
    url = f"{API_BASE}/serp/google/organic/live/advanced"
    body = [
        {
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": "desktop",
            "os": "windows",
            "depth": 20,
        }
    ]
    r = requests.post(url, json=body, auth=(login, password), timeout=90)
    r.raise_for_status()
    data = r.json()
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    res0 = (tasks[0].get("result") or [])
    if not res0:
        return []
    items = (res0[0].get("items") or [])
    # keep only organic items if present
    organic = [it for it in items if (it.get("type") or "").lower() in ["organic", "google_organic", "organic_extended"]]
    return organic or items


def main() -> int:
    ap = argparse.ArgumentParser(description="Build DataForSEO SERP rank snapshot for a keyword set.")
    ap.add_argument(
        "--project-root",
        default=str(Path.cwd()),
        help="Project root (to load .env)",
    )
    ap.add_argument(
        "--keywords-csv",
        default=os.environ.get("SEO_KEYWORDS_CSV", ""),
        help="CSV containing keywords to snapshot (or set SEO_KEYWORDS_CSV).",
    )
    ap.add_argument("--keywords-col", default="keyword", help="Column name in keywords CSV")
    ap.add_argument("--max-keywords", type=int, default=100, help="Max keywords to snapshot")
    ap.add_argument("--target-domain", default=os.environ.get("TARGET_DOMAIN", ""), help="Domain to find in SERP (or set TARGET_DOMAIN)")
    ap.add_argument("--output-dir", required=True, help="Directory to write CSVs")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)

    # Resolve defaults from project root if not explicitly provided
    if not args.keywords_csv:
        candidates = [
            os.path.join(args.project_root, "work/seo/plan/measurement_keywords.csv"),
            os.path.join(args.project_root, "work/seo/plan/Feb_2026_measurement_keywords.csv"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                args.keywords_csv = c
                break
    if not args.keywords_csv or not os.path.isfile(args.keywords_csv):
        raise SystemExit(
            "Missing keywords CSV.\n"
            "- Pass --keywords-csv /abs/path/to/keywords.csv, or\n"
            "- Set SEO_KEYWORDS_CSV, or\n"
            "- Place one at work/seo/plan/measurement_keywords.csv"
        )

    if not args.target_domain.strip():
        # best-effort derive from WP_SITE_URL if present
        wp_site = os.environ.get("WP_SITE_URL", "").strip()
        host = (urlparse(wp_site).hostname or "").lower()
        if host:
            args.target_domain = host
        else:
            raise SystemExit("Missing --target-domain (or set TARGET_DOMAIN, or set WP_SITE_URL so we can derive it).")

    login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
    password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD. Add them to .env (gitignored) or export them.")

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en").strip() or "en"

    kws = dedupe(read_keywords_from_csv(args.keywords_csv, args.keywords_col))[: max(1, int(args.max_keywords))]
    fetched_at = datetime.now(timezone.utc).isoformat()

    rows: List[Dict[str, object]] = []
    for kw in kws:
        items = dfs_serp_google_organic_live(
            login=login,
            password=password,
            keyword=kw,
            location_code=location_code,
            language_code=language_code,
        )
        pos, url, top_domains = parse_serp_find_domain(items, args.target_domain)
        rows.append(
            {
                "keyword": kw,
                "location_code": location_code,
                "language_code": language_code,
                "target_domain": args.target_domain,
                "best_position": pos if pos is not None else "",
                "best_url": url or "",
                "top_domains": top_domains,
                "fetched_at": fetched_at,
            }
        )

    out = os.path.join(args.output_dir, "Benchmark_DataForSEO_RankSnapshot.csv")
    write_csv(
        out,
        ["keyword", "location_code", "language_code", "target_domain", "best_position", "best_url", "top_domains", "fetched_at"],
        rows,
    )
    print(f"Wrote DataForSEO rank snapshot -> {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

