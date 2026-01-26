#!/usr/bin/env python3
"""
Create a SERP baseline table: top organic results per keyword.

Outputs (in --output-dir):
  - Benchmark_SERP_TopResults.csv
  - Benchmark_SERP_FeatureCounts.csv

This is complementary to Benchmark_DataForSEO_RankSnapshot.csv:
it captures who ranks, which URLs, and what SERP modules appear.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


def read_keywords(path: str, col: str) -> List[str]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        out: List[str] = []
        for row in r:
            kw = (row.get(col) or "").strip()
            if kw:
                out.append(kw)
        seen = set()
        ded = []
        for k in out:
            kl = k.lower()
            if kl in seen:
                continue
            seen.add(kl)
            ded.append(k)
        return ded


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def dfs_serp_google_organic_live(
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
    return res0[0].get("items") or []


def _infer_target_domain() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    return (urlparse(wp_site).hostname or "").strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser(description="Build SERP top-results baseline CSVs.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--keywords-csv", default="", help="Keywords CSV (defaults to work/seo/plan/measurement_keywords.csv if present)")
    ap.add_argument("--keywords-col", default="keyword")
    ap.add_argument("--max-keywords", type=int, default=60)
    ap.add_argument("--depth", type=int, default=10, help="Top N results to keep per keyword (default 10)")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)

    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD.")

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en") or "en").strip()
    target_domain = _infer_target_domain()

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
        raise SystemExit("Missing keywords CSV (use --keywords-csv or create work/seo/plan/measurement_keywords.csv).")

    kws = read_keywords(args.keywords_csv, args.keywords_col)[: max(1, int(args.max_keywords))]
    fetched_at = datetime.now(timezone.utc).isoformat()

    rows: List[Dict[str, object]] = []
    feature_counts: Counter[str] = Counter()

    keep_depth = max(1, int(args.depth))

    for kw in kws:
        items = dfs_serp_google_organic_live(
            login=login,
            password=password,
            keyword=kw,
            location_code=location_code,
            language_code=language_code,
            depth=max(keep_depth, 20),
        )

        for it in items:
            t = (it.get("type") or "").strip().lower()
            if t:
                feature_counts[t] += 1

        organic = [it for it in items if (it.get("type") or "").strip().lower() in {"organic", "google_organic", "organic_extended"}]
        organic = organic[:keep_depth]

        for it in organic:
            dom = (it.get("domain") or "").strip().lower()
            url = (it.get("url") or "").strip()
            title = (it.get("title") or "").strip()
            pos = it.get("rank_group") or it.get("rank_absolute") or ""
            rows.append(
                {
                    "keyword": kw,
                    "rank": pos,
                    "domain": dom,
                    "url": url,
                    "title": title,
                    "type": (it.get("type") or "").strip(),
                    "is_target_domain": "yes" if (target_domain and (dom == target_domain or dom.endswith("." + target_domain))) else "no",
                    "location_code": location_code,
                    "language_code": language_code,
                    "fetched_at": fetched_at,
                }
            )

    out_top = os.path.join(args.output_dir, "Benchmark_SERP_TopResults.csv")
    write_csv(
        out_top,
        ["keyword", "rank", "domain", "url", "title", "type", "is_target_domain", "location_code", "language_code", "fetched_at"],
        rows,
    )

    out_features = os.path.join(args.output_dir, "Benchmark_SERP_FeatureCounts.csv")
    feature_rows = [{"serp_item_type": k, "count": v, "fetched_at": fetched_at} for k, v in feature_counts.most_common()]
    write_csv(out_features, ["serp_item_type", "count", "fetched_at"], feature_rows)

    print(f"Wrote SERP top results -> {out_top} ({len(rows)} rows)")
    print(f"Wrote SERP feature counts -> {out_features} ({len(feature_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

