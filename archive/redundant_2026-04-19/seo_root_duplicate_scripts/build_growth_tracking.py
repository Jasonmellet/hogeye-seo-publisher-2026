#!/usr/bin/env python3
"""
Build weekly/monthly growth tracking templates from forecast scenarios.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import date, timedelta, datetime, timezone
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


def to_float(v: object, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def month_end(d: date) -> date:
    next_month = date(d.year + (1 if d.month == 12 else 0), 1 if d.month == 12 else d.month + 1, 1)
    return next_month - timedelta(days=1)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build weekly and monthly growth tracking templates.")
    ap.add_argument("--scenarios-csv", required=True, help="Path to Forecast_25pct_scenarios.csv")
    ap.add_argument("--output-dir", required=True, help="Directory to write tracking CSVs")
    ap.add_argument("--start-date", default="", help="Start date YYYY-MM-DD (default today)")
    ap.add_argument("--end-date", default="", help="End date YYYY-MM-DD (default 2026-05-31)")
    args = ap.parse_args()

    fetched_at = datetime.now(timezone.utc).isoformat()
    start = date.fromisoformat(args.start_date) if args.start_date else date.today()
    end = date.fromisoformat(args.end_date) if args.end_date else date(2026, 5, 31)

    rows = read_csv(args.scenarios_csv)
    base = next((r for r in rows if (r.get("scenario") or "").strip() == "base"), rows[0] if rows else None)
    if not base:
        raise SystemExit("No scenario rows found.")

    baseline_clicks = to_float(base.get("baseline_clicks_total"))
    projected_clicks = to_float(base.get("projected_clicks_total"))
    target_clicks = to_float(base.get("target_clicks_for_25pct"))

    # Weekly template
    weekly_rows: List[Dict[str, object]] = []
    week_idx = 1
    cursor = start
    while cursor <= end:
        week_end = min(cursor + timedelta(days=6), end)
        # linear guide between baseline and base projected clicks by end date
        progress = ((cursor - start).days / max(1, (end - start).days))
        expected_clicks = baseline_clicks + (projected_clicks - baseline_clicks) * progress
        weekly_rows.append(
            {
                "week_index": week_idx,
                "week_start": cursor.isoformat(),
                "week_end": week_end.isoformat(),
                "baseline_clicks_total": round(baseline_clicks, 2),
                "expected_clicks_total_base_path": round(expected_clicks, 2),
                "target_clicks_25pct": round(target_clicks, 2),
                "actual_clicks_total": "",
                "actual_impressions_total": "",
                "actual_ctr": "",
                "variance_vs_base_path": "",
                "variance_vs_25pct_target": "",
                "notes": "",
                "fetched_at": fetched_at,
            }
        )
        week_idx += 1
        cursor = week_end + timedelta(days=1)

    # Monthly checkpoints through end date
    monthly_rows: List[Dict[str, object]] = []
    month_cursor = date(start.year, start.month, 1)
    while month_cursor <= end:
        m_end = min(month_end(month_cursor), end)
        progress = ((m_end - start).days / max(1, (end - start).days))
        expected_clicks = baseline_clicks + (projected_clicks - baseline_clicks) * max(0.0, min(1.0, progress))
        monthly_rows.append(
            {
                "month": month_cursor.strftime("%Y-%m"),
                "checkpoint_date": m_end.isoformat(),
                "baseline_clicks_total": round(baseline_clicks, 2),
                "expected_clicks_total_base_path": round(expected_clicks, 2),
                "target_clicks_25pct": round(target_clicks, 2),
                "actual_clicks_total": "",
                "variance_vs_base_path": "",
                "variance_vs_25pct_target": "",
                "status": "",
                "notes": "",
                "fetched_at": fetched_at,
            }
        )
        month_cursor = date(month_cursor.year + (1 if month_cursor.month == 12 else 0), 1 if month_cursor.month == 12 else month_cursor.month + 1, 1)

    out_weekly = os.path.join(args.output_dir, "Forecast_25pct_weekly_tracking.csv")
    out_monthly = os.path.join(args.output_dir, "Forecast_25pct_monthly_checkpoints.csv")
    write_csv(
        out_weekly,
        [
            "week_index",
            "week_start",
            "week_end",
            "baseline_clicks_total",
            "expected_clicks_total_base_path",
            "target_clicks_25pct",
            "actual_clicks_total",
            "actual_impressions_total",
            "actual_ctr",
            "variance_vs_base_path",
            "variance_vs_25pct_target",
            "notes",
            "fetched_at",
        ],
        weekly_rows,
    )
    write_csv(
        out_monthly,
        [
            "month",
            "checkpoint_date",
            "baseline_clicks_total",
            "expected_clicks_total_base_path",
            "target_clicks_25pct",
            "actual_clicks_total",
            "variance_vs_base_path",
            "variance_vs_25pct_target",
            "status",
            "notes",
            "fetched_at",
        ],
        monthly_rows,
    )

    print(f"Wrote weekly tracking -> {out_weekly} ({len(weekly_rows)} rows)")
    print(f"Wrote monthly checkpoints -> {out_monthly} ({len(monthly_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

