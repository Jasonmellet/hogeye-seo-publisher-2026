#!/usr/bin/env python3
"""
Push SEO CSV datasets (generated locally) into a Google Sheet using a service account.

This avoids needing n8n UI access to load initial datasets.

Behavior (KISS):
  - For each dataset CSV, ensure the tab exists (create if missing)
  - Replace the entire tab with the CSV contents (header + rows)
  - Chunk writes to avoid API payload limits

Datasets pushed (by default):
  - semrush_landing_pages
  - semrush_queries_by_page
  - semrush_opportunities_nonbrand
  - semrush_cannibalization_nonbrand
  - plan_feb_2026_draft  (legacy example; customize for your client)
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def read_csv_values(path: str) -> List[List[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        return [[c if c is not None else "" for c in row] for row in reader]


def chunks(items: List[List[str]], size: int) -> Iterable[Tuple[int, List[List[str]]]]:
    for i in range(0, len(items), size):
        yield i, items[i : i + size]


def get_sheet_titles(svc, spreadsheet_id: str) -> Dict[str, int]:
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    out: Dict[str, int] = {}
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        title = props.get("title")
        sid = props.get("sheetId")
        if title is not None and sid is not None:
            out[str(title)] = int(sid)
    return out


def ensure_sheet(svc, spreadsheet_id: str, title: str) -> None:
    titles = get_sheet_titles(svc, spreadsheet_id)
    if title in titles:
        return
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()


def ensure_grid_size(svc, spreadsheet_id: str, title: str, min_rows: int, min_cols: int) -> None:
    """
    Google Sheets defaults new sheets to 1000 rows x 26 cols.
    For large datasets we must resize the sheet grid before writing values.
    """
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    cur_rows = None
    cur_cols = None
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") == title:
            sheet_id = props.get("sheetId")
            grid = props.get("gridProperties", {}) or {}
            cur_rows = grid.get("rowCount")
            cur_cols = grid.get("columnCount")
            break

    if sheet_id is None:
        raise RuntimeError(f"Sheet not found after ensure_sheet: {title}")

    target_rows = max(int(cur_rows or 0), int(min_rows))
    target_cols = max(int(cur_cols or 0), int(min_cols))
    if (cur_rows or 0) >= target_rows and (cur_cols or 0) >= target_cols:
        return

    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"rowCount": target_rows, "columnCount": target_cols},
                        },
                        "fields": "gridProperties(rowCount,columnCount)",
                    }
                }
            ]
        },
    ).execute()


def clear_sheet_values(values_svc, spreadsheet_id: str, title: str) -> None:
    # Clear whole sheet (A:Z…); Google ignores unused columns.
    values_svc.clear(spreadsheetId=spreadsheet_id, range=f"{title}!A:ZZ").execute()


def write_sheet_values(values_svc, spreadsheet_id: str, title: str, values: List[List[str]], chunk_size: int = 500) -> None:
    # Write in chunks starting at A1
    for offset, chunk in chunks(values, chunk_size):
        start_row = 1 + offset
        end_row = start_row + len(chunk) - 1
        # columns count based on first row
        col_count = max((len(r) for r in chunk), default=1)
        end_col_letter = col_to_a1(col_count)
        rng = f"{title}!A{start_row}:{end_col_letter}{end_row}"
        values_svc.update(
            spreadsheetId=spreadsheet_id,
            range=rng,
            valueInputOption="RAW",
            body={"values": chunk},
        ).execute()


def col_to_a1(n: int) -> str:
    # 1 -> A, 26 -> Z, 27 -> AA, etc.
    n = max(1, int(n))
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(ord("A") + r) + s
    return s


def _find_latest_subdir(parent: Path) -> Optional[Path]:
    """
    Return most recently modified direct subdirectory, or None.
    This keeps the script generic across clients without hardcoding Semrush export date ranges.
    """
    if not parent.exists() or not parent.is_dir():
        return None
    subs = [p for p in parent.iterdir() if p.is_dir()]
    if not subs:
        return None
    return sorted(subs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def dataset_paths(*, project_root: str, semrush_dir: str, plan_dir: str) -> Dict[str, str]:
    root = Path(project_root)
    semrush = Path(semrush_dir)
    plan = Path(plan_dir)

    # Allow semrush_dir/plan_dir to be relative to project_root
    if not semrush.is_absolute():
        semrush = root / semrush
    if not plan.is_absolute():
        plan = root / plan

    # Support either:
    # - semrush_dir points at the OTI export dir containing landing_pages.csv, queries_by_page.csv, etc
    # - semrush_dir points at work/seo/semrush/, in which case we select the latest subdir
    if semrush.is_dir() and not (semrush / "landing_pages.csv").is_file():
        latest = _find_latest_subdir(semrush)
        if latest:
            semrush = latest

    return {
        # Semrush (recommended)
        "semrush_landing_pages": str(semrush / "landing_pages.csv"),
        "semrush_queries_by_page": str(semrush / "queries_by_page.csv"),
        "semrush_opportunities_nonbrand": str(semrush / "opportunities_nonbrand.csv"),
        "semrush_cannibalization_nonbrand": str(semrush / "cannibalization_nonbrand.csv"),
        # Plan outputs (legacy Feb 2026 naming; keep as an example convention)
        "plan_feb_2026_draft": str(plan / "plan_feb_2026_draft.csv"),
        "Feb_2026_plan_constraints": str(plan / "Feb_2026_plan_constraints.csv"),
        "Feb_2026_clusters_candidates": str(plan / "Feb_2026_clusters_candidates.csv"),
        "Feb_2026_clusters_enriched": str(plan / "Feb_2026_clusters_enriched.csv"),
        "Feb_2026_plan_final": str(plan / "Feb_2026_plan_final.csv"),
        "Feb_2026_briefs": str(plan / "Feb_2026_briefs.csv"),
        "Feb_2026_execution_checklists": str(plan / "Feb_2026_execution_checklists.csv"),
        "Feb_2026_measurement_keywords": str(plan / "Feb_2026_measurement_keywords.csv"),
        "Feb_2026_measurement_weekly": str(plan / "Feb_2026_measurement_weekly.csv"),
    }


def benchmark_paths(benchmark_dir: str) -> Dict[str, str]:
    """
    Benchmark datasets are generated into a dated directory (work/seo/benchmark/YYYY-MM-DD/).
    We map those CSVs to stable tab names in the planning sheet.
    """
    return {
        "Benchmark_Summary": os.path.join(benchmark_dir, "Benchmark_Summary.csv"),
        "Benchmark_GSC_LandingPages": os.path.join(benchmark_dir, "Benchmark_GSC_LandingPages.csv"),
        "Benchmark_GSC_QueriesByPage": os.path.join(benchmark_dir, "Benchmark_GSC_QueriesByPage.csv"),
        "Benchmark_GSC_QueriesByPage_Brand": os.path.join(benchmark_dir, "Benchmark_GSC_QueriesByPage_Brand.csv"),
        "Benchmark_GA4_LandingPages": os.path.join(benchmark_dir, "Benchmark_GA4_LandingPages.csv"),
        "Benchmark_DataForSEO_RankSnapshot": os.path.join(benchmark_dir, "Benchmark_DataForSEO_RankSnapshot.csv"),
        "Benchmark_Sitemap_Inventory": os.path.join(benchmark_dir, "Benchmark_Sitemap_Inventory.csv"),
        "Benchmark_SERP_TopResults": os.path.join(benchmark_dir, "Benchmark_SERP_TopResults.csv"),
        "Benchmark_SERP_FeatureCounts": os.path.join(benchmark_dir, "Benchmark_SERP_FeatureCounts.csv"),
        # Optional, but useful for a "full" baseline:
        "Benchmark_SERP_CompetitorDomains": os.path.join(benchmark_dir, "Benchmark_SERP_CompetitorDomains.csv"),
        "Benchmark_Backlinks_RefDomains_Target": os.path.join(benchmark_dir, "Benchmark_Backlinks_RefDomains_Target.csv"),
        "Benchmark_Backlinks_RefDomains_Competitors": os.path.join(benchmark_dir, "Benchmark_Backlinks_RefDomains_Competitors.csv"),
        "Benchmark_Backlinks_GapDomains": os.path.join(benchmark_dir, "Benchmark_Backlinks_GapDomains.csv"),
        "Benchmark_OnPage_Summary": os.path.join(benchmark_dir, "Benchmark_OnPage_Summary.csv"),
        "Benchmark_OnPage_IssueCounts": os.path.join(benchmark_dir, "Benchmark_OnPage_IssueCounts.csv"),
        "Benchmark_OnPage_Pages": os.path.join(benchmark_dir, "Benchmark_OnPage_Pages.csv"),
        "Benchmark_OnPage_NonIndexable": os.path.join(benchmark_dir, "Benchmark_OnPage_NonIndexable.csv"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Push local SEO CSV datasets into a Google Sheet.")
    ap.add_argument("--spreadsheet-id", default=os.environ.get("SEO_SPREADSHEET_ID", ""), help="Google Sheet ID")
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        help="Path to Google service account JSON key",
    )
    ap.add_argument(
        "--project-root",
        default=str(Path.cwd()),
        help="Project root path (used to locate CSVs). Defaults to current working directory.",
    )
    ap.add_argument(
        "--semrush-dir",
        default=os.environ.get("SEMRUSH_OTI_DIR", "work/seo/semrush"),
        help="Semrush OTI export dir (or parent dir containing dated subdirs). Relative to project root by default.",
    )
    ap.add_argument(
        "--plan-dir",
        default=os.environ.get("SEO_PLAN_DIR", "work/seo/plan"),
        help="Plan CSV directory (relative to project root by default).",
    )
    ap.add_argument("--skip-big", action="store_true", help="Skip semrush_queries_by_page (largest tab)")
    ap.add_argument("--benchmark-dir", default="", help="Optional benchmark directory to also push (work/seo/benchmark/YYYY-MM-DD)")
    ap.add_argument(
        "--only-benchmark",
        action="store_true",
        help="Only push benchmark tabs (ignore Semrush/plan datasets). Requires --benchmark-dir.",
    )
    ap.add_argument("--chunk-size", type=int, default=500, help="Rows per Sheets update request")
    args = ap.parse_args()

    if not args.spreadsheet_id:
        raise SystemExit("Missing --spreadsheet-id (or set SEO_SPREADSHEET_ID).")

    if not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json\n"
            f"(got: {args.service_account_json or '(empty)'})"
        )

    paths: Dict[str, str]
    if args.only_benchmark:
        if not args.benchmark_dir:
            raise SystemExit("--only-benchmark requires --benchmark-dir.")
        if not os.path.isdir(args.benchmark_dir):
            raise SystemExit(f"--benchmark-dir not found: {args.benchmark_dir}")
        paths = {tab: path for tab, path in benchmark_paths(args.benchmark_dir).items() if os.path.isfile(path)}
    else:
        paths = dataset_paths(project_root=args.project_root, semrush_dir=args.semrush_dir, plan_dir=args.plan_dir)
        if args.skip_big:
            paths.pop("semrush_queries_by_page", None)

        if args.benchmark_dir:
            if not os.path.isdir(args.benchmark_dir):
                raise SystemExit(f"--benchmark-dir not found: {args.benchmark_dir}")
            # Merge benchmark datasets; only push files that exist
            for tab, path in benchmark_paths(args.benchmark_dir).items():
                if os.path.isfile(path):
                    paths[tab] = path

    creds = service_account.Credentials.from_service_account_file(args.service_account_json, scopes=SCOPES)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    values_svc = sheets.spreadsheets().values()

    for tab, path in paths.items():
        if not os.path.isfile(path):
            raise SystemExit(f"Missing dataset file for {tab}: {path}")

        print(f"-> {tab}: reading {path}")
        values = read_csv_values(path)
        if not values:
            print(f"   (empty CSV) skipping write")
            continue

        print(f"   ensuring tab exists...")
        ensure_sheet(sheets, args.spreadsheet_id, tab)
        # Ensure grid can hold all values
        max_cols = max((len(r) for r in values), default=1)
        ensure_grid_size(sheets, args.spreadsheet_id, tab, min_rows=len(values), min_cols=max_cols)
        print(f"   clearing tab...")
        clear_sheet_values(values_svc, args.spreadsheet_id, tab)
        print(f"   writing {len(values)} rows...")
        write_sheet_values(values_svc, args.spreadsheet_id, tab, values, chunk_size=args.chunk_size)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

