#!/usr/bin/env python3
"""
One-command present-state benchmark runner.

Generates a dated benchmark directory under:
  work/seo/benchmark/YYYY-MM-DD/

Then pushes benchmark outputs to the planning sheet using:
  scripts/seo/push_seo_csvs_to_sheet.py --benchmark-dir ...
"""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import date
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run GSC+GA4+DataForSEO benchmark and push to Sheets.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (defaults to current working directory)")
    ap.add_argument("--spreadsheet-id", default=os.environ.get("SEO_SPREADSHEET_ID", ""), help="Planning sheet ID")
    ap.add_argument("--site-url", default=os.environ.get("GSC_SITE_URL", ""), help="GSC property, e.g. sc-domain:example.com")
    ap.add_argument("--ga4-property-id", default=os.environ.get("GA4_PROPERTY_ID", ""), help="GA4 numeric property id")
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--top-pages", type=int, default=50)
    ap.add_argument("--top-queries-per-page", type=int, default=100)
    ap.add_argument("--brand-terms", default=os.environ.get("BRAND_TERMS", ""), help="Comma-separated brand tokens to exclude")
    ap.add_argument("--max-keywords", type=int, default=100)
    ap.add_argument(
        "--service-account-json",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    )
    ap.add_argument("--skip-push", action="store_true", help="Generate benchmark CSVs but do not push to Sheets")
    args = ap.parse_args()

    if not args.site_url.strip():
        raise SystemExit("Missing --site-url (or set GSC_SITE_URL). Example: GSC_SITE_URL=sc-domain:example.com")
    if not args.service_account_json or not os.path.isfile(args.service_account_json):
        raise SystemExit(
            "Missing service account JSON.\n"
            "- Set GOOGLE_APPLICATION_CREDENTIALS to a JSON key file, or\n"
            "- Pass --service-account-json /abs/path/to/key.json"
        )

    out_dir = os.path.join(args.project_root, "work/seo/benchmark", date.today().isoformat())
    os.makedirs(out_dir, exist_ok=True)

    py = os.path.join(args.project_root, ".venv/bin/python")
    if not os.path.isfile(py):
        py = "python3"

    # 1) GSC pull
    run(
        [
            py,
            os.path.join(args.project_root, "scripts/seo/gsc_benchmark_pull.py"),
            "--site-url",
            args.site_url,
            "--days",
            str(args.days),
            "--top-pages",
            str(args.top_pages),
            "--top-queries-per-page",
            str(args.top_queries_per_page),
            "--brand-terms",
            args.brand_terms,
            "--service-account-json",
            args.service_account_json,
            "--output-dir",
            out_dir,
        ]
    )

    # 2) GA4 pull (optional but requested)
    if args.ga4_property_id:
        run(
            [
                py,
                os.path.join(args.project_root, "scripts/seo/ga4_benchmark_pull.py"),
                "--property-id",
                args.ga4_property_id,
                "--days",
                str(args.days),
                "--top-pages",
                str(args.top_pages),
                "--service-account-json",
                args.service_account_json,
                "--output-dir",
                out_dir,
            ]
        )
    else:
        print("! Skipping GA4 pull (missing --ga4-property-id or GA4_PROPERTY_ID).")

    # 3) DataForSEO snapshot (uses Feb measurement keyword list by default)
    run(
        [
            py,
            os.path.join(args.project_root, "scripts/seo/dataforseo_benchmark_rank_snapshot.py"),
            "--project-root",
            args.project_root,
            "--max-keywords",
            str(args.max_keywords),
            "--output-dir",
            out_dir,
        ]
    )

    # 4) Summary
    run([py, os.path.join(args.project_root, "scripts/seo/build_benchmark_summary.py"), "--output-dir", out_dir])

    # 5) Push to sheet (benchmark tabs)
    if args.skip_push:
        print(f"Benchmark generated at: {out_dir} (push skipped)")
        return 0

    if not args.spreadsheet_id:
        raise SystemExit("Missing --spreadsheet-id (or set SEO_SPREADSHEET_ID).")

    run(
        [
            py,
            os.path.join(args.project_root, "scripts/seo/push_seo_csvs_to_sheet.py"),
            "--spreadsheet-id",
            args.spreadsheet_id,
            "--service-account-json",
            args.service_account_json,
            "--project-root",
            args.project_root,
            "--benchmark-dir",
            out_dir,
            "--skip-big",
        ]
    )

    print(f"Benchmark generated + pushed. Dir: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

