#!/usr/bin/env python3
"""
Build an executive benchmark summary from benchmark CSVs.

Inputs (in output-dir):
  - Benchmark_GSC_LandingPages.csv
  - Benchmark_GSC_QueriesByPage.csv
  - Benchmark_GA4_LandingPages.csv (optional)
  - Benchmark_DataForSEO_RankSnapshot.csv (optional)

Output:
  - Benchmark_Summary.csv
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


def read_csv_dicts(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def to_float(v: object) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def to_int(v: object) -> int:
    try:
        return int(float(v))
    except Exception:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Benchmark_Summary.csv from benchmark outputs.")
    ap.add_argument("--output-dir", required=True, help="Benchmark directory containing CSVs")
    ap.add_argument("--top-pages", type=int, default=20)
    ap.add_argument("--top-queries", type=int, default=50)
    # kept for backwards compatibility; currently not used in this script
    ap.add_argument("--target-domain", default=os.environ.get("TARGET_DOMAIN", ""), help="(optional) target domain (unused)")
    args = ap.parse_args()

    fetched_at = datetime.now(timezone.utc).isoformat()

    gsc_pages_path = os.path.join(args.output_dir, "Benchmark_GSC_LandingPages.csv")
    gsc_qbp_path = os.path.join(args.output_dir, "Benchmark_GSC_QueriesByPage.csv")
    ga4_path = os.path.join(args.output_dir, "Benchmark_GA4_LandingPages.csv")
    dfs_path = os.path.join(args.output_dir, "Benchmark_DataForSEO_RankSnapshot.csv")

    pages: List[Dict[str, str]] = []
    qbp: List[Dict[str, str]] = []
    has_gsc = os.path.isfile(gsc_pages_path) and os.path.isfile(gsc_qbp_path)
    if has_gsc:
        pages = read_csv_dicts(gsc_pages_path)
        qbp = read_csv_dicts(gsc_qbp_path)

    range_start = pages[0].get("range_start", "") if pages else ""
    range_end = pages[0].get("range_end", "") if pages else ""

    total_clicks = sum(to_float(r.get("clicks")) for r in pages) if has_gsc else 0.0
    total_impr = sum(to_float(r.get("impressions")) for r in pages) if has_gsc else 0.0
    total_ctr = (total_clicks / total_impr) if total_impr else 0.0
    avg_pos_weighted = 0.0
    if total_impr:
        avg_pos_weighted = sum(to_float(r.get("avg_position")) * to_float(r.get("impressions")) for r in pages) / total_impr

    # Top pages/queries only when GSC data exists
    pages_sorted = sorted(pages, key=lambda r: to_float(r.get("clicks")), reverse=True) if has_gsc else []
    top_pages = pages_sorted[: max(1, int(args.top_pages))] if has_gsc else []

    q_sorted = sorted(qbp, key=lambda r: to_float(r.get("clicks")), reverse=True) if has_gsc else []
    top_queries = q_sorted[: max(1, int(args.top_queries))] if has_gsc else []

    # Optional GA4 rollup
    ga4_sessions = ""
    if os.path.isfile(ga4_path):
        ga4 = read_csv_dicts(ga4_path)
        ga4_sessions = str(sum(to_float(r.get("sessions")) for r in ga4))

    # Optional DataForSEO rollup
    dfs_ranked = ""
    dfs_top10 = ""
    if os.path.isfile(dfs_path):
        dfs = read_csv_dicts(dfs_path)
        ranked = 0
        top10 = 0
        for r in dfs:
            pos = to_int(r.get("best_position"))
            if pos > 0:
                ranked += 1
                if pos <= 10:
                    top10 += 1
        dfs_ranked = str(ranked)
        dfs_top10 = str(top10)

    # Summary table as key/value rows (simple for exec consumption)
    out_rows: List[Dict[str, object]] = []
    if has_gsc:
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "range_start", "value": range_start, "fetched_at": fetched_at})
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "range_end", "value": range_end, "fetched_at": fetched_at})
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "clicks", "value": round(total_clicks, 2), "fetched_at": fetched_at})
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "impressions", "value": round(total_impr, 2), "fetched_at": fetched_at})
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "ctr", "value": round(total_ctr, 4), "fetched_at": fetched_at})
        out_rows.append({"section": "GSC Totals (Top Pages)", "metric": "avg_position_weighted", "value": round(avg_pos_weighted, 2), "fetched_at": fetched_at})
    else:
        out_rows.append(
            {
                "section": "GSC Totals (Top Pages)",
                "metric": "note",
                "value": "GSC benchmark CSVs missing; enable Search Console API + grant service account access, then re-run benchmark.",
                "fetched_at": fetched_at,
            }
        )

    if ga4_sessions != "":
        out_rows.append({"section": "GA4 Totals (Top Landing Pages)", "metric": "sessions", "value": ga4_sessions, "fetched_at": fetched_at})

    if dfs_ranked != "":
        out_rows.append({"section": "DataForSEO Rank Snapshot", "metric": "keywords_ranked", "value": dfs_ranked, "fetched_at": fetched_at})
        out_rows.append({"section": "DataForSEO Rank Snapshot", "metric": "keywords_in_top10", "value": dfs_top10, "fetched_at": fetched_at})

    # Top pages (flattened)
    for i, p in enumerate(top_pages, start=1):
        out_rows.append(
            {
                "section": "Top Pages (GSC)",
                "metric": f"page_{i}",
                "value": f"{p.get('page_url')} | clicks={p.get('clicks')} | impr={p.get('impressions')} | ctr={p.get('ctr')} | pos={p.get('avg_position')}",
                "fetched_at": fetched_at,
            }
        )

    # Top queries (flattened)
    for i, q in enumerate(top_queries, start=1):
        out_rows.append(
            {
                "section": "Top Non-Brand Queries (GSC)",
                "metric": f"query_{i}",
                "value": f"{q.get('query')} | page={q.get('page_url')} | clicks={q.get('clicks')} | impr={q.get('impressions')} | ctr={q.get('ctr')} | pos={q.get('avg_position')}",
                "fetched_at": fetched_at,
            }
        )

    out_path = os.path.join(args.output_dir, "Benchmark_Summary.csv")
    write_csv(out_path, ["section", "metric", "value", "fetched_at"], out_rows)
    print(f"Wrote benchmark summary -> {out_path} ({len(out_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

