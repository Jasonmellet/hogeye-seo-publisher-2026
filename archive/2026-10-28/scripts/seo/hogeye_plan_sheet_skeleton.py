#!/usr/bin/env python3
"""
Create a BB-style planning sheet skeleton (tabs only) for Hogeye:
- Overview
- Jan_2026 .. Jun_2026
- Technical_Plan

This does NOT generate content drafts or publish to WordPress.
It just creates the structure so we can paste/push datasets and decisions.
"""

from __future__ import annotations

import argparse
import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def ensure_sheet(sheets, spreadsheet_id: str, title: str) -> None:
    meta = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s.get("properties", {}).get("title") for s in (meta.get("sheets") or [])}
    if title in existing:
        return
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()


def write_header(values_svc, spreadsheet_id: str, title: str, header: List[str]) -> None:
    # Write only the header row (A1:...1). No clearing of existing data.
    end_col = chr(ord("A") + max(0, len(header) - 1))
    rng = f"{title}!A1:{end_col}1"
    values_svc.update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="RAW",
        body={"values": [header]},
    ).execute()


def main() -> int:
    ap = argparse.ArgumentParser(description="Create Hogeye Jan–Jun planning tabs in a Google Sheet.")
    ap.add_argument("--spreadsheet-id", default=os.environ.get("SEO_SPREADSHEET_ID", ""), required=False)
    ap.add_argument("--service-account-json", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""), required=False)
    args = ap.parse_args()

    if not args.spreadsheet_id:
        raise SystemExit("Missing --spreadsheet-id (or set SEO_SPREADSHEET_ID).")
    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit("Missing service account JSON (GOOGLE_APPLICATION_CREDENTIALS or --service-account-json).")

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    values_svc = sheets.spreadsheets().values()

    tabs = ["Overview", "Jan_2026", "Feb_2026", "Mar_2026", "Apr_2026", "May_2026", "Jun_2026", "Technical_Plan"]
    for t in tabs:
        ensure_sheet(sheets, args.spreadsheet_id, t)

    write_header(
        values_svc,
        args.spreadsheet_id,
        "Overview",
        ["section", "metric", "value", "source", "notes", "updated_at"],
    )
    month_header = ["type", "title", "primary_keyword", "target_url", "notes", "status", "owner", "due_date"]
    for t in ["Jan_2026", "Feb_2026", "Mar_2026", "Apr_2026", "May_2026", "Jun_2026"]:
        write_header(values_svc, args.spreadsheet_id, t, month_header)
    write_header(
        values_svc,
        args.spreadsheet_id,
        "Technical_Plan",
        ["month", "priority", "issue", "evidence", "fix", "scope", "owner", "status"],
    )

    print("OK: created/verified tabs + wrote headers")
    print("spreadsheet_id:", args.spreadsheet_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

