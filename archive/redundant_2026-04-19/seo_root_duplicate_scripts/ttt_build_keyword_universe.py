#!/usr/bin/env python3
"""
Build a first-pass keyword universe for a site using DataForSEO.

Outputs (CSV) under work/seo/plan/ (git-ignored), prefixed by --client-key:
  - {client}_keywords_for_site.csv
  - {client}_keywords_expanded.csv         (optional expansion via keywords_for_keywords)
  - {client}_keywords_cluster_candidates.csv (simple heuristic clusters for planning)

This is intentionally lightweight: it gets us usable, DataForSEO-backed data
even before GSC/GA4 access is available.

Notes:
  - DataForSEO Google Ads Live endpoints have strict per-account limits
    (docs mention ~12 requests/min for keywords_for_site / keywords_for_keywords).
    Keep --expand-requests low.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _chunks(seq: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _dedupe(seq: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in seq:
        k = s.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(s.strip())
    return out


def _infer_domain_from_env() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    host = (urlparse(wp_site).hostname or "").strip().lower()
    return host


def _dfs_post(login: str, password: str, path: str, payload: list[dict], timeout: int = 90) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.post(url, json=payload, auth=(login, password), timeout=timeout)
    r.raise_for_status()
    return r.json()


def dfs_keywords_for_site_live(
    *,
    login: str,
    password: str,
    target_domain: str,
    location_code: int,
    language_code: str,
    target_type: str = "site",
) -> List[dict]:
    data = _dfs_post(
        login,
        password,
        "/keywords_data/google_ads/keywords_for_site/live",
        [
            {
                "target": target_domain,
                "target_type": target_type,
                "location_code": location_code,
                "language_code": language_code,
            }
        ],
        timeout=120,
    )
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    return tasks[0].get("result") or []


def dfs_keywords_for_keywords_live(
    *,
    login: str,
    password: str,
    keywords: List[str],
    location_code: int,
    language_code: str,
    sort_by: str = "relevance",
) -> List[dict]:
    data = _dfs_post(
        login,
        password,
        "/keywords_data/google_ads/keywords_for_keywords/live",
        [
            {
                "keywords": keywords,
                "location_code": location_code,
                "language_code": language_code,
                "sort_by": sort_by,
            }
        ],
        timeout=120,
    )
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    return tasks[0].get("result") or []


def _normalize_kw(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _cluster_key(keyword: str) -> str:
    # Tiny heuristic: cluster by first 2 tokens after removing a few stopwords.
    stop = {"a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "with", "near"}
    toks = [t for t in re.split(r"[^a-z0-9]+", _normalize_kw(keyword)) if t and t not in stop]
    if not toks:
        return ""
    return " ".join(toks[:2]) if len(toks) >= 2 else toks[0]


def _clean_client_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a keyword universe via DataForSEO.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--client-key", default="client", help="Prefix for output files, e.g. bb, hogeye, bpt")
    ap.add_argument("--target-domain", default="", help="Target domain (defaults to WP_SITE_URL host)")
    ap.add_argument("--location-code", type=int, default=0, help="Override DATAFORSEO_LOCATION_CODE")
    ap.add_argument("--language-code", default="", help="Override DATAFORSEO_LANGUAGE_CODE")
    ap.add_argument("--output-dir", default="work/seo/plan", help="Where to write outputs (default work/seo/plan)")
    ap.add_argument("--max-site-keywords", type=int, default=1500, help="Cap keywords_for_site result rows")

    ap.add_argument(
        "--expand",
        action="store_true",
        help="Also expand using keywords_for_keywords/live using top site keywords as seeds.",
    )
    ap.add_argument(
        "--seed-keywords",
        default="",
        help="Optional comma-separated seed keywords to use for expansion instead of site keywords.",
    )
    ap.add_argument(
        "--seed-csv",
        default="",
        help="Optional CSV path containing seed keywords (overrides --seed-keywords).",
    )
    ap.add_argument(
        "--seed-col",
        default="keyword",
        help="Column name for --seed-csv (default: keyword).",
    )
    ap.add_argument(
        "--expand-seeds",
        type=int,
        default=20,
        help="How many top site keywords to use as expansion seeds (default 20).",
    )
    ap.add_argument(
        "--expand-requests",
        type=int,
        default=1,
        help="How many expansion requests to run (each request can include up to 20 seed keywords). Default 1.",
    )
    ap.add_argument(
        "--expand-sort-by",
        default="relevance",
        choices=["relevance", "search_volume", "competition_index", "low_top_of_page_bid", "high_top_of_page_bid"],
        help="Sort keywords_for_keywords results.",
    )
    ap.add_argument(
        "--cluster-min-size",
        type=int,
        default=5,
        help="Minimum keywords per cluster to keep (default 5).",
    )
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)

    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD (set in .env).")

    client_key = _clean_client_key(args.client_key)
    location_code = args.location_code or int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (args.language_code or os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en")).strip() or "en"

    target_domain = (args.target_domain or _infer_domain_from_env()).strip().lower().lstrip(".")
    if not target_domain:
        raise SystemExit("Missing --target-domain and could not infer from WP_SITE_URL.")

    fetched_at = datetime.now(timezone.utc).isoformat()

    # 1) Keywords for site
    site_rows = dfs_keywords_for_site_live(
        login=login,
        password=password,
        target_domain=target_domain,
        location_code=location_code,
        language_code=language_code,
        target_type="site",
    )[: max(1, int(args.max_site_keywords))]

    out_site = os.path.join(args.output_dir, f"{client_key}_keywords_for_site.csv")
    _write_csv(
        out_site,
        [
            "keyword",
            "search_volume",
            "cpc",
            "competition",
            "competition_index",
            "low_top_of_page_bid",
            "high_top_of_page_bid",
            "location_code",
            "language_code",
            "target_domain",
            "fetched_at",
        ],
        [
            {
                "keyword": r.get("keyword"),
                "search_volume": r.get("search_volume"),
                "cpc": r.get("cpc"),
                "competition": r.get("competition"),
                "competition_index": r.get("competition_index"),
                "low_top_of_page_bid": r.get("low_top_of_page_bid"),
                "high_top_of_page_bid": r.get("high_top_of_page_bid"),
                "location_code": location_code,
                "language_code": language_code,
                "target_domain": target_domain,
                "fetched_at": fetched_at,
            }
            for r in site_rows
            if (r.get("keyword") or "").strip()
        ],
    )

    # 2) Optional expansion
    expanded_rows: List[dict] = []
    if args.expand:
        seeds: List[str] = []
        if (args.seed_csv or "").strip():
            with open(args.seed_csv, "r", encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                seeds = _dedupe([(row.get(args.seed_col) or "") for row in r])
        elif (args.seed_keywords or "").strip():
            seeds = _dedupe([s for s in args.seed_keywords.split(",")])
        else:
            seeds = _dedupe([(r.get("keyword") or "") for r in site_rows])

        # Respect requested cap (keeps API usage predictable)
        seeds = seeds[: max(1, int(args.expand_seeds))]
        reqs = max(1, int(args.expand_requests))
        seed_batches = list(_chunks(seeds, 20))[:reqs]
        for batch in seed_batches:
            expanded_rows.extend(
                dfs_keywords_for_keywords_live(
                    login=login,
                    password=password,
                    keywords=batch,
                    location_code=location_code,
                    language_code=language_code,
                    sort_by=args.expand_sort_by,
                )
            )

        by_kw: Dict[str, dict] = {}
        for r in expanded_rows:
            kw = (r.get("keyword") or "").strip()
            if not kw:
                continue
            k = kw.lower()
            if k not in by_kw:
                by_kw[k] = r
        expanded_rows = list(by_kw.values())

        out_expanded = os.path.join(args.output_dir, f"{client_key}_keywords_expanded.csv")
        _write_csv(
            out_expanded,
            [
                "keyword",
                "search_volume",
                "cpc",
                "competition",
                "competition_index",
                "low_top_of_page_bid",
                "high_top_of_page_bid",
                "location_code",
                "language_code",
                "target_domain",
                "fetched_at",
            ],
            [
                {
                    "keyword": r.get("keyword"),
                    "search_volume": r.get("search_volume"),
                    "cpc": r.get("cpc"),
                    "competition": r.get("competition"),
                    "competition_index": r.get("competition_index"),
                    "low_top_of_page_bid": r.get("low_top_of_page_bid"),
                    "high_top_of_page_bid": r.get("high_top_of_page_bid"),
                    "location_code": location_code,
                    "language_code": language_code,
                    "target_domain": target_domain,
                    "fetched_at": fetched_at,
                }
                for r in expanded_rows
                if (r.get("keyword") or "").strip()
            ],
        )

    # 3) Cluster candidates (simple heuristic)
    all_keywords = _dedupe([(r.get("keyword") or "") for r in site_rows] + [(r.get("keyword") or "") for r in expanded_rows])
    buckets: Dict[str, List[str]] = defaultdict(list)
    for kw in all_keywords:
        ck = _cluster_key(kw)
        if not ck:
            continue
        buckets[ck].append(kw)

    cluster_min = max(2, int(args.cluster_min_size))
    cluster_items: List[Tuple[str, List[str]]] = [(k, v) for k, v in buckets.items() if len(v) >= cluster_min]
    cluster_items.sort(key=lambda kv: (-len(kv[1]), kv[0]))

    out_clusters = os.path.join(args.output_dir, f"{client_key}_keywords_cluster_candidates.csv")
    rows: List[Dict[str, object]] = []
    for i, (ck, kws) in enumerate(cluster_items, start=1):
        primary = kws[0]
        supporting = " | ".join(kws[1 : min(len(kws), 15)])
        rows.append(
            {
                "cluster_id": f"{client_key}_{i:04d}",
                "status": "candidate",
                "cluster_key": ck,
                "primary_keyword": primary,
                "supporting_keywords": supporting,
                "notes": "Auto-generated cluster (review/merge/split manually).",
                "location_code": location_code,
                "language_code": language_code,
                "target_domain": target_domain,
                "fetched_at": fetched_at,
            }
        )

    _write_csv(
        out_clusters,
        [
            "cluster_id",
            "status",
            "cluster_key",
            "primary_keyword",
            "supporting_keywords",
            "notes",
            "location_code",
            "language_code",
            "target_domain",
            "fetched_at",
        ],
        rows,
    )

    print("OK")
    print("wrote:", out_site)
    if args.expand:
        print("wrote:", os.path.join(args.output_dir, f"{client_key}_keywords_expanded.csv"))
    print("wrote:", out_clusters)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

