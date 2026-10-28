#!/usr/bin/env python3
"""
Create a spreadsheet-ready Feb 2026 plan constraints CSV.

This locks the planning guardrails (KPI, non-brand) and bucket counts (A/B/C).
Counts are defaults and can be edited later in the sheet; this file is the baseline.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import List


def write_csv(path: str, fieldnames: List[str], rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 plan constraints CSV.")
    ap.add_argument("--output", required=True, help="Path to write Feb_2026_plan_constraints.csv")
    ap.add_argument("--month", default="2026-02", help="Month (YYYY-MM)")
    ap.add_argument("--primary-kpi", default="qualified_leads", help="Primary KPI identifier")
    ap.add_argument("--bucket-a-new-posts", type=int, default=4, help="Bucket A count (net-new posts)")
    ap.add_argument("--bucket-b-major-updates", type=int, default=4, help="Bucket B count (major page updates)")
    ap.add_argument("--bucket-c-supporting", type=int, default=2, help="Bucket C count (support pages)")
    args = ap.parse_args()

    total = args.bucket_a_new_posts + args.bucket_b_major_updates + args.bucket_c_supporting
    fetched_at = datetime.now(timezone.utc).isoformat()

    rows = [
        {
            "month": args.month,
            "primary_kpi": args.primary_kpi,
            "non_brand_only": "TRUE",
            "brand_exclusion_terms": "lakota",
            "bucket_a_new_posts": args.bucket_a_new_posts,
            "bucket_b_major_page_updates": args.bucket_b_major_updates,
            "bucket_c_supporting_pages": args.bucket_c_supporting,
            "total_assets_target": total,
            "notes": (
                "Defaults can be edited. Guardrails: non-brand only; every asset must include a qualified-lead CTA "
                "(tour, request info, enroll). Homepage remains primary for 'summer camps in new york' cluster."
            ),
            "fetched_at": fetched_at,
        }
    ]

    write_csv(
        args.output,
        [
            "month",
            "primary_kpi",
            "non_brand_only",
            "brand_exclusion_terms",
            "bucket_a_new_posts",
            "bucket_b_major_page_updates",
            "bucket_c_supporting_pages",
            "total_assets_target",
            "notes",
            "fetched_at",
        ],
        rows,
    )
    print(f"Wrote constraints -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

