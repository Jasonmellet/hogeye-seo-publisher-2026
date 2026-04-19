#!/usr/bin/env python3
"""
Select the final Feb 2026 plan (exactly 10 assets) from cluster candidates + constraints.

This version uses Semrush-derived signals (impressions, position) and bucket constraints.
DataForSEO enrichment can be layered later; the plan remains review-first.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple


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


def to_int(v: str) -> int:
    s = (v or "").strip().replace(",", "")
    try:
        return int(float(s)) if s else 0
    except ValueError:
        return 0


def to_float(v: str) -> float:
    s = (v or "").strip().replace(",", "")
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def score(row: Dict[str, str]) -> float:
    """
    Lead-oriented heuristic:
      - higher impressions -> higher priority
      - better (lower) position -> easier win
      - Major page updates tend to convert better, but we enforce bucket counts separately
    """
    impr = to_int(row.get("total_impressions", ""))
    pos = to_float(row.get("best_position", ""))
    # DataForSEO enrichment (optional): if present, blend in search volume
    dfs_sv = to_int(row.get("dfs_cluster_search_volume_sum", "")) or to_int(row.get("dfs_primary_search_volume", "")) or 0
    dfs_comp = to_float(row.get("dfs_cluster_competition_avg", "")) or to_float(row.get("dfs_primary_competition", "")) or 0.0
    pos_factor = 0.0
    if pos > 0:
        # closer to top gets a slight boost
        pos_factor = max(0.0, (20.0 - min(pos, 20.0)) / 20.0)
    # Weighted blend:
    # - Semrush impressions = immediate opportunity (already showing)
    # - DataForSEO volume = longer-term demand (cluster size)
    # - Competition mildly downweights
    return (float(impr) * (1.0 + 0.25 * pos_factor)) + (float(dfs_sv) * (1.0 - min(max(dfs_comp, 0.0), 1.0)) * 0.25)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 plan final (10 assets).")
    ap.add_argument("--constraints", required=True, help="Path to Feb_2026_plan_constraints.csv")
    ap.add_argument("--clusters", required=True, help="Path to Feb_2026_clusters_candidates.csv")
    ap.add_argument("--output", required=True, help="Path to write Feb_2026_plan_final.csv")
    args = ap.parse_args()

    constraints = read_csv(args.constraints)
    if not constraints:
        raise SystemExit("Constraints file is empty.")
    c = constraints[0]

    target_total = to_int(c.get("total_assets_target", "10")) or 10
    bucket_a = to_int(c.get("bucket_a_new_posts", "0"))
    bucket_b = to_int(c.get("bucket_b_major_page_updates", "0"))
    bucket_c = to_int(c.get("bucket_c_supporting_pages", "0"))

    clusters = [r for r in read_csv(args.clusters) if (r.get("status") or "").strip().lower() == "candidate"]
    # Sort by score desc
    clusters_sorted = sorted(clusters, key=lambda r: score(r), reverse=True)

    # Allocate by bucket constraints
    picked: List[Dict[str, str]] = []
    bucket_counts = {"Bucket_A_NewPosts": 0, "Bucket_B_MajorPageUpdates": 0, "Bucket_C_SupportingPages": 0}
    bucket_limits = {"Bucket_A_NewPosts": bucket_a, "Bucket_B_MajorPageUpdates": bucket_b, "Bucket_C_SupportingPages": bucket_c}

    for r in clusters_sorted:
        b = (r.get("bucket_candidate") or "").strip()
        if b not in bucket_limits:
            continue
        if bucket_counts[b] >= bucket_limits[b]:
            continue
        picked.append(r)
        bucket_counts[b] += 1
        if len(picked) >= target_total:
            break

    # If still short (e.g., limits sum < target_total), fill remaining by best score regardless of bucket
    if len(picked) < target_total:
        picked_ids = {r.get("cluster_id") for r in picked}
        for r in clusters_sorted:
            if r.get("cluster_id") in picked_ids:
                continue
            picked.append(r)
            if len(picked) >= target_total:
                break

    fetched_at = datetime.now(timezone.utc).isoformat()
    out_rows: List[Dict[str, object]] = []
    for i, r in enumerate(picked, start=1):
        out_rows.append(
            {
                "month": r.get("month") or "2026-02",
                "rank": i,
                "bucket": r.get("bucket_candidate"),
                "cluster_id": r.get("cluster_id"),
                "primary_target_url": r.get("primary_target_url"),
                "primary_keyword": r.get("primary_keyword"),
                "supporting_keywords": r.get("supporting_keywords"),
                "total_impressions": to_int(r.get("total_impressions", "")),
                "best_position": to_float(r.get("best_position", "")),
                "recommended_cta": r.get("recommended_cta"),
                "status": "planned",
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
            "supporting_keywords",
            "total_impressions",
            "best_position",
            "recommended_cta",
            "status",
            "fetched_at",
        ],
        out_rows,
    )
    print(f"Wrote final plan -> {args.output} ({len(out_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

