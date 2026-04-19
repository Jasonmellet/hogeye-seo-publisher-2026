#!/usr/bin/env python3
"""
Find query cannibalization from Semrush OTI normalized exports (queries_by_page.csv).

Outputs a CSV listing queries that appear on multiple URLs with meaningful impressions.
Designed for quick SEO triage: pick a primary page per query and de-conflict the rest.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from typing import Dict, List, Tuple


def is_nonbrand(query: str, brand_terms: List[str]) -> bool:
    q = (query or "").lower()
    return all(term.lower() not in q for term in brand_terms)


def to_int(s: str) -> int:
    try:
        return int(float((s or "").replace(",", "").strip()))
    except ValueError:
        return 0


def to_float(s: str) -> float:
    try:
        return float((s or "").replace(",", "").strip())
    except ValueError:
        return 0.0


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Find query cannibalization from Semrush OTI queries_by_page.csv")
    ap.add_argument("--input", required=True, help="Path to queries_by_page.csv")
    ap.add_argument("--output", required=True, help="Path to write cannibalization_report.csv")
    ap.add_argument("--min-impressions", type=int, default=50, help="Min impressions per URL row to consider")
    ap.add_argument("--top", type=int, default=200, help="Max queries in output")
    ap.add_argument(
        "--brand-term",
        action="append",
        default=["lakota"],
        help="Brand term(s) to exclude (repeat flag to add more). Default: lakota",
    )
    args = ap.parse_args()

    groups: Dict[str, List[Dict[str, object]]] = defaultdict(list)

    with open(args.input, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            query = (row.get("query") or "").strip()
            if not query:
                continue
            if not is_nonbrand(query, args.brand_term):
                continue

            impressions = to_int(row.get("impressions", ""))
            if impressions < args.min_impressions:
                continue

            url = (row.get("url_canonical") or "").strip()
            if not url:
                continue

            groups[query.lower()].append(
                {
                    "query": query,
                    "url_canonical": url,
                    "impressions": impressions,
                    "clicks": to_int(row.get("clicks", "")),
                    "ctr_pct": to_float(row.get("ctr_pct", "")),
                    "position": to_float(row.get("position", "")),
                }
            )

    # Keep only queries that map to multiple URLs
    items: List[Tuple[int, str, List[Dict[str, object]]]] = []
    for qkey, rows in groups.items():
        urls = {r["url_canonical"] for r in rows}
        if len(urls) < 2:
            continue
        total_impr = sum(int(r["impressions"]) for r in rows)
        items.append((total_impr, qkey, rows))

    items.sort(key=lambda t: t[0], reverse=True)
    items = items[: max(0, args.top)]

    out_rows: List[Dict[str, object]] = []
    for total_impr, _qkey, rows in items:
        # sort URL rows by impressions desc
        rows_sorted = sorted(rows, key=lambda r: int(r["impressions"]), reverse=True)
        urls = " | ".join(str(r["url_canonical"]) for r in rows_sorted)
        url_impressions = " | ".join(str(r["impressions"]) for r in rows_sorted)
        url_positions = " | ".join(f'{r["position"]:.1f}' for r in rows_sorted)
        out_rows.append(
            {
                "query": rows_sorted[0]["query"],
                "total_impressions": total_impr,
                "urls": urls,
                "impressions_by_url": url_impressions,
                "positions_by_url": url_positions,
            }
        )

    write_csv(
        args.output,
        ["query", "total_impressions", "urls", "impressions_by_url", "positions_by_url"],
        out_rows,
    )
    print(f"Cannibalization queries: {len(out_rows)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

