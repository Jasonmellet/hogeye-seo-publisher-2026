#!/usr/bin/env python3
"""
Build an execution checklist tab for Feb 2026 assets.

Output: work/seo/plan/Feb_2026_execution_checklists.csv

Each row is a checklist item tied to a plan rank + cluster_id.
This makes execution predictable and reduces \"going in circles\" during publishing.
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


def add(rows: List[Dict[str, object]], *, month: str, rank: str, cluster_id: str, asset: str, target_url: str, phase: str, step: str) -> None:
    rows.append(
        {
            "month": month,
            "rank": rank,
            "cluster_id": cluster_id,
            "asset": asset,
            "target_url": target_url,
            "phase": phase,
            "step": step,
            "status": "todo",
            "owner": "Jason",
            "notes": "",
        }
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 execution checklist CSV.")
    ap.add_argument("--plan", required=True, help="Path to Feb_2026_plan_final.csv")
    ap.add_argument("--briefs", required=True, help="Path to Feb_2026_briefs.csv")
    ap.add_argument("--output", required=True, help="Path to write Feb_2026_execution_checklists.csv")
    args = ap.parse_args()

    plan = read_csv(args.plan)
    briefs = { (r.get("cluster_id") or "").strip(): r for r in read_csv(args.briefs) }
    fetched_at = datetime.now(timezone.utc).isoformat()

    rows: List[Dict[str, object]] = []

    for p in plan:
        month = p.get("month") or "2026-02"
        rank = p.get("rank") or ""
        cid = (p.get("cluster_id") or "").strip()
        target_url = p.get("primary_target_url") or ""
        primary_kw = p.get("primary_keyword") or ""
        bucket = p.get("bucket") or ""
        asset = f"{bucket} — {primary_kw}".strip(" —")

        b = briefs.get(cid, {})
        cta_primary_url = b.get("cta_primary_url") or os.environ.get("CTA_PRIMARY_URL", "")
        cta_secondary_url = b.get("cta_secondary_url") or os.environ.get("CTA_SECONDARY_URL", "")

        # Preflight / safety
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Preflight", step="Confirm target URL and scope (page update vs new post).")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Preflight", step="Take a manual screenshot/notes of critical sections that must not change (especially homepage countdown/widget areas).")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Preflight", step="Confirm CTAs: Primary=Request Info, Secondary=Enroll Now.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Preflight", step=f"Verify CTA URLs: {cta_primary_url} and {cta_secondary_url}.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Preflight", step="Run publisher in safe mode: it will create a local JSON backup of the current WP page before updating.")

        # Drafting
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Draft", step="Draft/update H1 + first 2 paragraphs to match non-brand intent.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Draft", step="Implement the brief outline (H2s) and add trust elements (care model, supervision, safety).")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Draft", step="Add FAQ section where appropriate (focus on parent objections that block Request Info).")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Draft", step="Add internal links to: homepage, sleepaway hub, dates/tuition, Request Info, Enroll Now (as applicable).")

        # Review
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Review", step="Spell/format check + ensure no duplicate/cannibalizing headings.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Review", step="Confirm Request Info CTA appears above the fold and at least once near the end.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Review", step="Confirm Enroll Now CTA appears (secondary) without overpowering Request Info.")

        # Publish protocol (to avoid circles)
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Publish", step="Run WordPress connection test (pre-publish).")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Publish", step="Publish via pipeline (one item at a time): verify output, then proceed to the next item.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Publish", step="Post-publish: re-check protected homepage markers (countdown/year) did not change.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Publish", step="Post-publish: confirm live CTAs route correctly (Request Info form, Enroll Now page).")

        # Measurement
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Measure", step="Log baseline (before publish) in Feb_2026_measurement_weekly.")
        add(rows, month=month, rank=rank, cluster_id=cid, asset=asset, target_url=target_url, phase="Measure", step="7 days after publish: record impressions/clicks/CTR/position and MQL change.")

    write_csv(
        args.output,
        ["month", "rank", "cluster_id", "asset", "target_url", "phase", "step", "status", "owner", "notes", "fetched_at"],
        [{**r, "fetched_at": fetched_at} for r in rows],
    )
    print(f"Wrote execution checklist -> {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

