#!/usr/bin/env python3
"""
Create execution briefs (spreadsheet rows) for each item in Feb_2026_plan_final.

These are concise, structured briefs you can hand to a writer/editor before any publishing.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
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


def suggest_title(primary_kw: str, bucket: str) -> str:
    kw = (primary_kw or "").strip()
    if bucket == "Bucket_A_NewPosts":
        return f"{kw.title()}: A Practical Guide for Parents (2026)"
    if bucket == "Bucket_C_SupportingPages":
        return f"{kw.title()} (FAQ + Quick Answers)"
    return f"{kw.title()} | Camp Lakota"


def suggest_outline(primary_kw: str) -> str:
    kw = (primary_kw or "").strip()
    return " | ".join(
        [
            f"What to know about {kw}",
            "Who it’s for (ages, fit, goals)",
            "Location & travel (NY / upstate context)",
            "Program highlights + daily life",
            "Safety & supervision (trust signals)",
            "Dates, tuition, and how to apply",
            "FAQs",
        ]
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 briefs from plan final.")
    ap.add_argument("--input", required=True, help="Path to Feb_2026_plan_final.csv")
    ap.add_argument("--output", required=True, help="Path to write Feb_2026_briefs.csv")
    args = ap.parse_args()

    plan = read_csv(args.input)
    fetched_at = datetime.now(timezone.utc).isoformat()

    rows: List[Dict[str, object]] = []
    for r in plan:
        bucket = r.get("bucket") or ""
        primary_kw = r.get("primary_keyword") or ""
        cta_primary_url = os.environ.get("CTA_PRIMARY_URL", "").strip()
        cta_secondary_url = os.environ.get("CTA_SECONDARY_URL", "").strip()
        rows.append(
            {
                "month": r.get("month") or "2026-02",
                "rank": r.get("rank"),
                "bucket": bucket,
                "cluster_id": r.get("cluster_id"),
                "primary_target_url": r.get("primary_target_url"),
                "primary_keyword": primary_kw,
                "working_title": suggest_title(primary_kw, bucket),
                "outline_h2s": suggest_outline(primary_kw),
                "cta_primary": "Request Info (MQL)",
                "cta_primary_url": cta_primary_url,
                "cta_secondary": "Enroll Now (CampBrain)",
                "cta_secondary_url": cta_secondary_url,
                "internal_links_to_add": "Homepage | Dates & Tuition | Enroll Now | Tours",
                "notes": "Draft brief skeleton. Refine with DataForSEO SERP format + competitor review before writing.",
                "status": "ready_for_brief_review",
                "fetched_at": fetched_at,
            }
        )

    write_csv(
        args.output,
        [
            "month",
            "rank",
            "bucket",
            "cluster_id",
            "primary_target_url",
            "primary_keyword",
            "working_title",
            "outline_h2s",
            "cta_primary",
            "cta_primary_url",
            "cta_secondary",
            "cta_secondary_url",
            "internal_links_to_add",
            "notes",
            "status",
            "fetched_at",
        ],
        rows,
    )
    print(f"Wrote briefs -> {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

