#!/usr/bin/env python3
"""
Push growth scorecard CSV tabs to Google Sheets.
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Dict, Iterable, List, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def read_csv_values(path: str) -> List[List[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return [list(row) for row in csv.reader(f)]


def chunks(items: List[List[str]], size: int) -> Iterable[Tuple[int, List[List[str]]]]:
    for i in range(0, len(items), size):
        yield i, items[i : i + size]


def col_to_a1(n: int) -> str:
    n = max(1, int(n))
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(ord("A") + r) + s
    return s


def get_sheet_titles(svc, spreadsheet_id: str) -> Dict[str, int]:
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    out: Dict[str, int] = {}
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") is not None and props.get("sheetId") is not None:
            out[str(props["title"])] = int(props["sheetId"])
    return out


def ensure_sheet(svc, spreadsheet_id: str, title: str) -> None:
    if title in get_sheet_titles(svc, spreadsheet_id):
        return
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()


def clear_sheet(values_svc, spreadsheet_id: str, title: str) -> None:
    values_svc.clear(spreadsheetId=spreadsheet_id, range=f"{title}!A:ZZ").execute()


def write_sheet(values_svc, spreadsheet_id: str, title: str, values: List[List[str]], chunk_size: int = 500) -> None:
    for offset, chunk in chunks(values, chunk_size):
        start_row = 1 + offset
        end_row = start_row + len(chunk) - 1
        max_cols = max((len(r) for r in chunk), default=1)
        rng = f"{title}!A{start_row}:{col_to_a1(max_cols)}{end_row}"
        values_svc.update(
            spreadsheetId=spreadsheet_id,
            range=rng,
            valueInputOption="RAW",
            body={"values": chunk},
        ).execute()


def main() -> int:
    ap = argparse.ArgumentParser(description="Push growth scorecard CSV datasets into Sheets tabs.")
    ap.add_argument("--spreadsheet-id", required=True)
    ap.add_argument("--service-account-json", required=True)
    ap.add_argument("--plan-dir", default="work/seo/plan", help="Directory with forecast/tracking CSVs")
    ap.add_argument("--chunk-size", type=int, default=500)
    args = ap.parse_args()

    if not os.path.isfile(args.service_account_json):
        raise SystemExit(f"Service account JSON not found: {args.service_account_json}")

    tab_to_file = {
        "Growth_Forecast_Scenarios": os.path.join(args.plan_dir, "Forecast_25pct_scenarios.csv"),
        "Growth_Forecast_KeywordModel": os.path.join(args.plan_dir, "Forecast_25pct_keyword_model.csv"),
        "Growth_Weekly_Tracking": os.path.join(args.plan_dir, "Forecast_25pct_weekly_tracking.csv"),
        "Growth_Monthly_Checkpoints": os.path.join(args.plan_dir, "Forecast_25pct_monthly_checkpoints.csv"),
    }

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    values_svc = sheets.spreadsheets().values()

    for tab, path in tab_to_file.items():
        if not os.path.isfile(path):
            raise SystemExit(f"Missing CSV for tab {tab}: {path}")
        values = read_csv_values(path)
        ensure_sheet(sheets, args.spreadsheet_id, tab)
        clear_sheet(values_svc, args.spreadsheet_id, tab)
        write_sheet(values_svc, args.spreadsheet_id, tab, values, chunk_size=args.chunk_size)
        print(f"Pushed {tab} <- {path} ({len(values)} rows)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

