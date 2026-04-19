#!/usr/bin/env python3
"""
Pull a present-state benchmark from GA4 (Google Analytics Data API).

Outputs (CSV):
  - Benchmark_GA4_LandingPages.csv

Requires:
  - Service account JSON with access to the GA4 property
  - GA4 Data API enabled in the GCP project
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest


SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Pull GA4 benchmark (landing pages).")
    ap.add_argument("--property-id", default=os.environ.get("GA4_PROPERTY_ID", ""), help="GA4 numeric property id")
    ap.add_argument("--days", type=int, default=28, help="Lookback window length")
    ap.add_argument("--end-date", default="", help="YYYY-MM-DD (defaults to yesterday)")
    ap.add_argument("--top-pages", type=int, default=50, help="Top landing pages")
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    )
    ap.add_argument("--output-dir", required=True, help="Directory to write CSVs")
    args = ap.parse_args()

    if not args.property_id.strip():
        raise SystemExit("Missing GA4 property id. Provide --property-id or set GA4_PROPERTY_ID.")

    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json"
        )

    end = date.fromisoformat(args.end_date) if args.end_date else (date.today() - timedelta(days=1))
    start = end - timedelta(days=max(1, args.days))
    fetched_at = datetime.now(timezone.utc).isoformat()

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    client = BetaAnalyticsDataClient(credentials=creds)

    # Keep it simple and robust: use a common landing page dimension.
    # If your GA4 config differs, we can adjust later.
    dimensions = [Dimension(name="landingPagePlusQueryString")]
    metrics = [Metric(name="sessions"), Metric(name="engagedSessions"), Metric(name="engagementRate"), Metric(name="conversions")]

    try:
        req = RunReportRequest(
            property=f"properties/{args.property_id}",
            date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
            dimensions=dimensions,
            metrics=metrics,
            limit=int(args.top_pages),
        )
        resp = client.run_report(req)
    except Exception:
        # Fallback: conversions metric can be missing depending on property/config.
        metrics = [Metric(name="sessions"), Metric(name="engagedSessions"), Metric(name="engagementRate")]
        try:
            req = RunReportRequest(
                property=f"properties/{args.property_id}",
                date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
                dimensions=dimensions,
                metrics=metrics,
                limit=int(args.top_pages),
            )
            resp = client.run_report(req)
        except Exception as e2:
            raise SystemExit(
                "Failed to query GA4. Ensure:\n"
                "- GA4 Data API is enabled in the service account project\n"
                "- Service account email has access to the GA4 property\n"
                f"Error: {e2}"
            )

    rows: List[Dict[str, object]] = []
    for r in resp.rows:
        dim_vals = [d.value for d in r.dimension_values]
        met_vals = [m.value for m in r.metric_values]
        landing = dim_vals[0] if dim_vals else ""
        out = {
            "range_start": start.isoformat(),
            "range_end": end.isoformat(),
            "landing_page": landing,
            "fetched_at": fetched_at,
        }
        # Map metrics in order (safe)
        for idx, m in enumerate(resp.metric_headers):
            out[m.name] = met_vals[idx] if idx < len(met_vals) else ""
        rows.append(out)

    out_path = os.path.join(args.output_dir, "Benchmark_GA4_LandingPages.csv")
    # Fieldnames: fixed ordering
    fieldnames = ["range_start", "range_end", "landing_page", "sessions", "engagedSessions", "engagementRate", "conversions", "fetched_at"]
    # Some properties won’t return conversions; keep column anyway.
    write_csv(out_path, fieldnames, rows)
    print(f"Wrote GA4 benchmark -> {out_path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

