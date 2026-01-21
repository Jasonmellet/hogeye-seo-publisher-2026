#!/usr/bin/env python3
"""
Import (copy) the MQL tracking sheet into the main planning spreadsheet.

Approach (simple + reliable):
  - Copy the entire source spreadsheet into the destination spreadsheet
  - Then rename the copied sheet to a stable tab name (e.g. mql_tracker_import)

Requirements:
  - Both spreadsheets must be shared with the same service account.
"""

from __future__ import annotations

import argparse
import os
from typing import Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheet_id_by_title(svc, spreadsheet_id: str, title: str) -> int | None:
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in meta.get("sheets", []):
        props = s.get("properties", {}) or {}
        if props.get("title") == title:
            return props.get("sheetId")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Import MQL tracker sheet into planning spreadsheet.")
    ap.add_argument("--source-spreadsheet-id", required=True, help="MQL tracker spreadsheet ID")
    ap.add_argument("--dest-spreadsheet-id", required=True, help="Planning spreadsheet ID")
    ap.add_argument("--source-sheet-title", default=None, help="Optional: limit to one tab by title (else copy first tab)")
    ap.add_argument("--dest-sheet-title", default="mql_tracker_import", help="Destination tab name")
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        help="Path to service account JSON",
    )
    args = ap.parse_args()

    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json"
        )

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    src_meta = svc.spreadsheets().get(spreadsheetId=args.source_spreadsheet_id).execute()
    src_sheets = src_meta.get("sheets", []) or []
    if not src_sheets:
        raise SystemExit("Source spreadsheet has no sheets.")

    if args.source_sheet_title:
        src_sheet_id = get_sheet_id_by_title(svc, args.source_spreadsheet_id, args.source_sheet_title)
        if src_sheet_id is None:
            raise SystemExit(f"Source sheet title not found: {args.source_sheet_title}")
    else:
        src_sheet_id = int(src_sheets[0].get("properties", {}).get("sheetId"))

    # Copy sheet into destination spreadsheet
    copy_resp = (
        svc.spreadsheets()
        .sheets()
        .copyTo(
            spreadsheetId=args.source_spreadsheet_id,
            sheetId=src_sheet_id,
            body={"destinationSpreadsheetId": args.dest_spreadsheet_id},
        )
        .execute()
    )
    new_sheet_id = int(copy_resp.get("sheetId"))

    # Rename the copied sheet
    svc.spreadsheets().batchUpdate(
        spreadsheetId=args.dest_spreadsheet_id,
        body={
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": new_sheet_id, "title": args.dest_sheet_title},
                        "fields": "title",
                    }
                }
            ]
        },
    ).execute()

    print(f"Copied sheetId={src_sheet_id} to dest as '{args.dest_sheet_title}' (newSheetId={new_sheet_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

