#!/usr/bin/env python3
"""
Pull a present-state benchmark from Google Search Console (GSC).

Outputs (CSV):
  - Benchmark_GSC_LandingPages.csv
  - Benchmark_GSC_QueriesByPage.csv

Requires:
  - Service account JSON with access to the property
  - GSC API enabled in the GCP project
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def is_brand_query(q: str, brand_terms: List[str]) -> bool:
    ql = (q or "").lower()
    return any(bt.strip().lower() in ql for bt in brand_terms if bt.strip())


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def ymd(d: date) -> str:
    return d.isoformat()


def main() -> int:
    ap = argparse.ArgumentParser(description="Pull GSC benchmark (landing pages + queries-by-page).")
    ap.add_argument("--site-url", default=os.environ.get("GSC_SITE_URL", ""), help="GSC property, e.g. sc-domain:example.com")
    ap.add_argument("--days", type=int, default=28, help="Lookback window length")
    ap.add_argument("--end-date", default="", help="YYYY-MM-DD (defaults to yesterday)")
    ap.add_argument("--top-pages", type=int, default=50, help="Top pages to pull sitewide")
    ap.add_argument("--top-queries-per-page", type=int, default=100, help="Queries per page")
    ap.add_argument("--brand-terms", default=os.environ.get("BRAND_TERMS", ""), help="Comma-separated brand tokens to exclude")
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    )
    ap.add_argument("--output-dir", required=True, help="Directory to write CSVs")
    args = ap.parse_args()

    if not args.site_url.strip():
        raise SystemExit("Missing --site-url (or set GSC_SITE_URL). Example: GSC_SITE_URL=sc-domain:example.com")
    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json"
        )

    end = date.fromisoformat(args.end_date) if args.end_date else (date.today() - timedelta(days=1))
    start = end - timedelta(days=max(1, args.days))
    fetched_at = datetime.now(timezone.utc).isoformat()

    brand_terms = [t.strip() for t in (args.brand_terms or "").split(",") if t.strip()]

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    # 1) Top pages sitewide
    try:
        resp = (
            svc.searchanalytics()
            .query(
                siteUrl=args.site_url,
                body={
                    "startDate": ymd(start),
                    "endDate": ymd(end),
                    "dimensions": ["page"],
                    "rowLimit": int(args.top_pages),
                },
            )
            .execute()
        )
    except Exception as e:
        raise SystemExit(
            "Failed to query GSC. Ensure:\n"
            "- Search Console API is enabled in the service account project\n"
            "- Service account email is added to the GSC property\n"
            f"Error: {e}"
        )

    page_rows: List[Dict[str, object]] = []
    pages: List[str] = []
    for row in resp.get("rows", []) or []:
        keys = row.get("keys") or []
        page = keys[0] if keys else ""
        pages.append(page)
        page_rows.append(
            {
                "range_start": ymd(start),
                "range_end": ymd(end),
                "page_url": page,
                "clicks": row.get("clicks"),
                "impressions": row.get("impressions"),
                "ctr": row.get("ctr"),
                "avg_position": row.get("position"),
                "fetched_at": fetched_at,
            }
        )

    # 2) Queries per page (non-brand)
    qbp_rows: List[Dict[str, object]] = []
    for page in pages:
        if not page:
            continue
        resp2 = (
            svc.searchanalytics()
            .query(
                siteUrl=args.site_url,
                body={
                    "startDate": ymd(start),
                    "endDate": ymd(end),
                    "dimensions": ["query"],
                    "rowLimit": int(args.top_queries_per_page),
                    "dimensionFilterGroups": [
                        {
                            "filters": [
                                {"dimension": "page", "operator": "equals", "expression": page},
                            ]
                        }
                    ],
                },
            )
            .execute()
        )
        for row in resp2.get("rows", []) or []:
            keys = row.get("keys") or []
            query = keys[0] if keys else ""
            if not query or is_brand_query(query, brand_terms):
                continue
            qbp_rows.append(
                {
                    "range_start": ymd(start),
                    "range_end": ymd(end),
                    "page_url": page,
                    "query": query,
                    "clicks": row.get("clicks"),
                    "impressions": row.get("impressions"),
                    "ctr": row.get("ctr"),
                    "avg_position": row.get("position"),
                    "fetched_at": fetched_at,
                }
            )

    out_pages = os.path.join(args.output_dir, "Benchmark_GSC_LandingPages.csv")
    out_qbp = os.path.join(args.output_dir, "Benchmark_GSC_QueriesByPage.csv")

    write_csv(
        out_pages,
        ["range_start", "range_end", "page_url", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        page_rows,
    )
    write_csv(
        out_qbp,
        ["range_start", "range_end", "page_url", "query", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        qbp_rows,
    )

    print(f"Wrote GSC benchmark -> {out_pages} ({len(page_rows)} rows), {out_qbp} ({len(qbp_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

