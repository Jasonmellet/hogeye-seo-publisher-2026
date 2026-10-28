#!/usr/bin/env python3
"""
Create measurement scaffolding for Feb 2026 plan.

Outputs:
  - Feb_2026_measurement_keywords.csv: keyword list to track (non-brand)
  - Feb_2026_measurement_weekly.csv: weekly snapshot template
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import Dict, List


def read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 measurement templates.")
    ap.add_argument("--plan", required=True, help="Path to Feb_2026_plan_final.csv")
    ap.add_argument("--outdir", required=True, help="Directory to write measurement CSVs")
    args = ap.parse_args()

    plan = read_csv(args.plan)
    fetched_at = datetime.now(timezone.utc).isoformat()

    kw_rows: List[Dict[str, object]] = []
    for r in plan:
        kw = (r.get("primary_keyword") or "").strip()
        if not kw:
            continue
        kw_rows.append(
            {
                "month": r.get("month") or "2026-02",
                "cluster_id": r.get("cluster_id"),
                "primary_target_url": r.get("primary_target_url"),
                "keyword": kw,
                "track_in_rank_tracker": "TRUE",
                "track_in_gsc": "TRUE",
                "notes": "Non-brand keyword. Baseline values should be captured before publishing changes.",
                "fetched_at": fetched_at,
            }
        )

    weekly_rows = [
        {
            "week_start": "",
            "week_end": "",
            "page_url": "",
            "keyword": "",
            "gsc_impressions": "",
            "gsc_clicks": "",
            "gsc_ctr": "",
            "gsc_avg_position": "",
            "organic_sessions": "",
            "qualified_leads": "",
            "notes": "",
            "fetched_at": fetched_at,
        }
    ]

    out_keywords = os.path.join(args.outdir, "Feb_2026_measurement_keywords.csv")
    out_weekly = os.path.join(args.outdir, "Feb_2026_measurement_weekly.csv")

    write_csv(
        out_keywords,
        [
            "month",
            "cluster_id",
            "primary_target_url",
            "keyword",
            "track_in_rank_tracker",
            "track_in_gsc",
            "notes",
            "fetched_at",
        ],
        kw_rows,
    )
    write_csv(
        out_weekly,
        [
            "week_start",
            "week_end",
            "page_url",
            "keyword",
            "gsc_impressions",
            "gsc_clicks",
            "gsc_ctr",
            "gsc_avg_position",
            "organic_sessions",
            "qualified_leads",
            "notes",
            "fetched_at",
        ],
        weekly_rows,
    )

    print(f"Wrote measurement -> {out_keywords} ({len(kw_rows)} rows), {out_weekly}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

