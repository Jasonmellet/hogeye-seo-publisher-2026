#!/usr/bin/env python3
"""
Delete unneeded Google Sheet tabs and reorder remaining tabs by importance.

Designed for a Feb plan spreadsheet. Uses service account auth.

Defaults:
  - Keeps only the tabs needed for the current Feb planning workflow + your working inputs.
  - Reorders so the first tabs are: Feb_2026_plan_final, Feb_2026_briefs, Feb_2026_clusters_enriched, ...

Safety:
  - Supports --dry-run to preview deletes/reorder without applying changes.
"""

from __future__ import annotations

import argparse
import os
from typing import Dict, List, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_meta(svc, spreadsheet_id: str) -> dict:
    return svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()


def get_sheets(meta: dict) -> List[dict]:
    return meta.get("sheets", []) or []


def sheet_map(meta: dict) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for s in get_sheets(meta):
        props = s.get("properties", {}) or {}
        title = props.get("title")
        if title:
            out[str(title)] = props
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Clean up and reorder tabs in a Google Sheet.")
    ap.add_argument("--spreadsheet-id", required=True, help="Spreadsheet ID")
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        help="Path to service account JSON",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions without applying changes")
    args = ap.parse_args()

    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json"
        )

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    meta = get_meta(svc, args.spreadsheet_id)
    title = meta.get("properties", {}).get("title")
    sheets = sheet_map(meta)

    # Keep set: only what we need for the current workflow + your working tabs.
    keep = {
        # Planning outputs (final)
        "Feb_2026_plan_final",
        "Feb_2026_briefs",
        "Feb_2026_clusters_enriched",
        "Feb_2026_plan_constraints",
        "Feb_2026_measurement_keywords",
        "Feb_2026_measurement_weekly",
        # Evidence (non-brand distilled)
        "semrush_opportunities_nonbrand",
        "semrush_cannibalization_nonbrand",
        # Working inputs you already have
        "sitemap_inventory",
        "keyword_suggestions_raw",
        "seed_keywords",
        "content_backlog_feb ",
        "mql_tracker_import",
    }

    # Delete list = anything not in keep.
    to_delete: List[Tuple[str, int]] = []
    for t, props in sheets.items():
        if t not in keep:
            to_delete.append((t, int(props["sheetId"])))

    # Reorder list (importance)
    desired_order = [
        "Feb_2026_plan_final",
        "Feb_2026_briefs",
        "mql_tracker_import",
        "Feb_2026_clusters_enriched",
        "Feb_2026_plan_constraints",
        "Feb_2026_measurement_keywords",
        "Feb_2026_measurement_weekly",
        "content_backlog_feb ",
        "sitemap_inventory",
        "keyword_suggestions_raw",
        "seed_keywords",
        "semrush_opportunities_nonbrand",
        "semrush_cannibalization_nonbrand",
    ]

    print(f"Spreadsheet: {title} ({args.spreadsheet_id})")
    print("Will delete:")
    for t, _sid in sorted(to_delete, key=lambda x: x[0].lower()):
        print(f"- {t}")

    print("\nWill keep + reorder (front-to-back):")
    for t in desired_order:
        if t in sheets:
            print(f"- {t}")

    if args.dry_run:
        print("\nDry run: no changes applied.")
        return 0

    requests = []
    for _t, sid in to_delete:
        requests.append({"deleteSheet": {"sheetId": sid}})

    # Re-read meta after deletes? We can set indices in same batchUpdate; Sheets API applies sequentially.
    # Build updateSheetProperties for those that exist.
    # Only reorder kept sheets that are present; any kept but missing are ignored.
    idx = 0
    for t in desired_order:
        props = sheets.get(t)
        if not props:
            continue
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": int(props["sheetId"]), "index": idx},
                    "fields": "index",
                }
            }
        )
        idx += 1

    if not requests:
        print("No changes needed.")
        return 0

    svc.spreadsheets().batchUpdate(spreadsheetId=args.spreadsheet_id, body={"requests": requests}).execute()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

