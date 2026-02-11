#!/usr/bin/env python3
"""
Deeper GSC export for planning (free data).

Why this exists:
- The benchmark pull intentionally samples (top pages + top queries per page).
- For planning, we often want larger *sitewide* exports:
  - Top queries (sitewide)
  - Top pages (sitewide)
  - Page+query pairs (sitewide)

Outputs (CSV) in --output-dir:
- GSC_Pages.csv
- GSC_Queries_NonBrand.csv
- GSC_Queries_Brand.csv
- GSC_PageQuery_NonBrand.csv
- GSC_PageQuery_Brand.csv

Notes:
- GSC Search Analytics API returns the "top" rows for the given dimensions.
- This uses pagination (startRow) so we can pull more than one page of results.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
REPO_ROOT = Path(__file__).resolve().parents[2]


def _is_brand_query(q: str, brand_terms: List[str]) -> bool:
    ql = (q or "").lower()
    return any(bt.strip().lower() in ql for bt in brand_terms if bt.strip())


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _ymd(d: date) -> str:
    return d.isoformat()


def _query_paginated(
    *,
    svc,
    site_url: str,
    start_date: date,
    end_date: date,
    dimensions: List[str],
    row_limit: int,
    max_rows: int,
    dimension_filter_groups: List[dict] | None = None,
) -> List[dict]:
    out: List[dict] = []
    start_row = 0
    while True:
        body: dict = {
            "startDate": _ymd(start_date),
            "endDate": _ymd(end_date),
            "dimensions": dimensions,
            "rowLimit": int(row_limit),
            "startRow": int(start_row),
        }
        if dimension_filter_groups:
            body["dimensionFilterGroups"] = dimension_filter_groups

        resp = svc.searchanalytics().query(siteUrl=site_url, body=body).execute()
        rows = resp.get("rows", []) or []
        out.extend(rows)

        if len(out) >= max_rows:
            return out[:max_rows]
        if len(rows) < row_limit:
            return out
        start_row += row_limit


def main() -> int:
    load_dotenv(REPO_ROOT / ".env", override=False)

    ap = argparse.ArgumentParser(description="Deep GSC export (sitewide queries/pages/page+query).")
    ap.add_argument("--site-url", default=os.environ.get("GSC_SITE_URL", ""), help="GSC property, e.g. sc-domain:example.com")
    ap.add_argument("--days", type=int, default=365, help="Lookback window length")
    ap.add_argument("--end-date", default="", help="YYYY-MM-DD (defaults to yesterday)")
    ap.add_argument("--brand-terms", default=os.environ.get("BRAND_TERMS", ""), help="Comma-separated brand tokens")
    ap.add_argument("--service-account-json", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--row-limit", type=int, default=25000, help="GSC API rowLimit per request (max 25000)")
    ap.add_argument("--max-rows", type=int, default=25000, help="Safety cap across pagination per dataset")
    args = ap.parse_args()

    if not args.site_url.strip():
        raise SystemExit("Missing --site-url (or set GSC_SITE_URL).")
    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit("Missing service account JSON (GOOGLE_APPLICATION_CREDENTIALS or --service-account-json).")

    end = date.fromisoformat(args.end_date) if args.end_date else (date.today() - timedelta(days=1))
    start = end - timedelta(days=max(1, int(args.days)))
    fetched_at = datetime.now(timezone.utc).isoformat()

    brand_terms = [t.strip() for t in (args.brand_terms or "").split(",") if t.strip()]

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    row_limit = max(1, min(25000, int(args.row_limit)))
    max_rows = max(1, int(args.max_rows))

    # Pages (sitewide)
    pages_rows = _query_paginated(
        svc=svc,
        site_url=args.site_url,
        start_date=start,
        end_date=end,
        dimensions=["page"],
        row_limit=row_limit,
        max_rows=max_rows,
    )
    pages_out: List[Dict[str, object]] = []
    for r in pages_rows:
        keys = r.get("keys") or []
        pages_out.append(
            {
                "range_start": _ymd(start),
                "range_end": _ymd(end),
                "page_url": keys[0] if keys else "",
                "clicks": r.get("clicks"),
                "impressions": r.get("impressions"),
                "ctr": r.get("ctr"),
                "avg_position": r.get("position"),
                "fetched_at": fetched_at,
            }
        )
    _write_csv(
        os.path.join(args.output_dir, "GSC_Pages.csv"),
        ["range_start", "range_end", "page_url", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        pages_out,
    )

    # Queries (sitewide)
    queries_rows = _query_paginated(
        svc=svc,
        site_url=args.site_url,
        start_date=start,
        end_date=end,
        dimensions=["query"],
        row_limit=row_limit,
        max_rows=max_rows,
    )
    nonbrand_out: List[Dict[str, object]] = []
    brand_out: List[Dict[str, object]] = []
    for r in queries_rows:
        keys = r.get("keys") or []
        q = keys[0] if keys else ""
        if not q:
            continue
        row_obj = {
            "range_start": _ymd(start),
            "range_end": _ymd(end),
            "query": q,
            "clicks": r.get("clicks"),
            "impressions": r.get("impressions"),
            "ctr": r.get("ctr"),
            "avg_position": r.get("position"),
            "fetched_at": fetched_at,
        }
        (brand_out if _is_brand_query(q, brand_terms) else nonbrand_out).append(row_obj)

    _write_csv(
        os.path.join(args.output_dir, "GSC_Queries_NonBrand.csv"),
        ["range_start", "range_end", "query", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        nonbrand_out,
    )
    _write_csv(
        os.path.join(args.output_dir, "GSC_Queries_Brand.csv"),
        ["range_start", "range_end", "query", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        brand_out,
    )

    # Page+Query (sitewide)
    pq_rows = _query_paginated(
        svc=svc,
        site_url=args.site_url,
        start_date=start,
        end_date=end,
        dimensions=["page", "query"],
        row_limit=row_limit,
        max_rows=max_rows,
    )
    pq_nonbrand: List[Dict[str, object]] = []
    pq_brand: List[Dict[str, object]] = []
    for r in pq_rows:
        keys = r.get("keys") or []
        page = keys[0] if len(keys) > 0 else ""
        q = keys[1] if len(keys) > 1 else ""
        if not q:
            continue
        row_obj = {
            "range_start": _ymd(start),
            "range_end": _ymd(end),
            "page_url": page,
            "query": q,
            "clicks": r.get("clicks"),
            "impressions": r.get("impressions"),
            "ctr": r.get("ctr"),
            "avg_position": r.get("position"),
            "fetched_at": fetched_at,
        }
        (pq_brand if _is_brand_query(q, brand_terms) else pq_nonbrand).append(row_obj)

    _write_csv(
        os.path.join(args.output_dir, "GSC_PageQuery_NonBrand.csv"),
        ["range_start", "range_end", "page_url", "query", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        pq_nonbrand,
    )
    _write_csv(
        os.path.join(args.output_dir, "GSC_PageQuery_Brand.csv"),
        ["range_start", "range_end", "page_url", "query", "clicks", "impressions", "ctr", "avg_position", "fetched_at"],
        pq_brand,
    )

    print("OK deep export")
    print("range:", _ymd(start), "->", _ymd(end))
    print("pages_rows:", len(pages_out))
    print("queries_nonbrand_rows:", len(nonbrand_out), "queries_brand_rows:", len(brand_out))
    print("pagequery_nonbrand_rows:", len(pq_nonbrand), "pagequery_brand_rows:", len(pq_brand))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

