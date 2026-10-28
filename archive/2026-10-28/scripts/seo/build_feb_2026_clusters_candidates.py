#!/usr/bin/env python3
"""
Convert plan_feb_2026_draft (query rows) into cluster candidates (asset-level rows).

Goal: produce spreadsheet rows that are closer to "things we will publish" than raw keywords.
This is intentionally heuristic; DataForSEO enrichment will validate volume/SERP before finalizing.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


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


def choose_primary_keyword(keywords: List[Tuple[str, int, float]]) -> str:
    # Prefer highest impressions; tie-break by best (lowest) position.
    keywords_sorted = sorted(keywords, key=lambda t: (-t[1], t[2] if t[2] > 0 else 9999))
    return keywords_sorted[0][0] if keywords_sorted else ""


def cluster_key(row: Dict[str, str]) -> str:
    """
    Create cluster keys that tend to become publishable assets.
    - Keep homepage terms together (one major update cluster)
    - Split sleepaway hub into subclusters by theme for easier asset planning
    """
    theme = (row.get("theme") or "").strip()
    primary_url = (row.get("primary_target_url") or "").strip()
    q = (row.get("query") or "").lower().replace("+", " ").strip()

    # Post-intent clusters (net-new blog posts). These should NOT live on the homepage/hub as a single mega-page.
    # We still keep them connected to the lead funnel via internal links + CTA.
    if any(w in q for w in ["affordable", "cost", "prices", "how much"]):
        return "post::sleepaway_cost_affordable"
    if any(w in q for w in ["best ", "top "]):
        if "summer" in q:
            return "post::best_summer_camps_ny"
        return "post::best_sleepaway_camps_ny"
    if any(w in q for w in ["2 week", "two week", "one week", "1 week", "short session"]):
        return "post::short_session_sleepaway"
    if any(w in q for w in ["for teens", "teen "]):
        return "post::sleepaway_for_teens"
    if any(w in q for w in ["for kids"]):
        return "post::sleepaway_for_kids"
    if any(w in q for w in ["boys", "girls", "coed"]):
        return "post::sleepaway_gender_or_coed"

    home_url = (os.environ.get("HOMEPAGE_URL") or os.environ.get("WP_SITE_URL") or "").strip()
    if home_url:
        # Normalize for compare (strip trailing slash)
        if primary_url.rstrip("/") == home_url.rstrip("/"):
            # Keep the homepage cluster focused on big head-term intent + lead CTA.
            return "homepage_summer_camp"

    if "upstate-ny-camp" in primary_url:
        if theme in ("coed_sleepaway",):
            return "sleepaway_hub_coed"
        if theme in ("sleepaway_teens", "sleepaway_kids"):
            return "sleepaway_hub_age_intent"
        if theme in ("near_me",):
            return "sleepaway_hub_near_me"
        if "2 week" in (row.get("query") or "").lower() or "one week" in (row.get("query") or "").lower():
            return "sleepaway_hub_short_sessions"
        if "best" in (row.get("query") or "").lower() or "top" in (row.get("query") or "").lower():
            return "sleepaway_hub_comparisons"
        return "sleepaway_hub_core"

    # Fallback: one cluster per primary URL
    return f"url::{primary_url}"


def bucket_candidate_for_cluster(cluster_id: str) -> str:
    # Heuristic: homepage + sleepaway hub clusters are major updates; others may become new/support content.
    if cluster_id.startswith("post::"):
        return "Bucket_A_NewPosts"
    if cluster_id.startswith("homepage_") or cluster_id.startswith("sleepaway_hub_"):
        return "Bucket_B_MajorPageUpdates"
    if cluster_id.startswith("url::"):
        return "Bucket_C_SupportingPages"
    return "Bucket_A_NewPosts"


def lead_cta_for_cluster(cluster_id: str) -> str:
    # KPI is qualified leads: bias toward Tour / Request Info, plus Enroll where appropriate.
    if cluster_id.startswith("homepage_"):
        return "Primary: Request Info (/request-info/) | Secondary: Enroll Now (/enroll-now/)"
    if cluster_id.startswith("sleepaway_hub_"):
        return "Primary: Request Info (/request-info/) | Secondary: Enroll Now (/enroll-now/)"
    if cluster_id.startswith("post::"):
        return "Primary: Request Info (/request-info/) | Secondary: Enroll Now (/enroll-now/)"
    return "Request info"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 cluster candidates from draft plan.")
    ap.add_argument("--input", required=True, help="Path to plan_feb_2026_draft.csv")
    ap.add_argument("--output", required=True, help="Path to write Feb_2026_clusters_candidates.csv")
    ap.add_argument("--month", default="2026-02", help="Month (YYYY-MM)")
    ap.add_argument(
        "--support-templates-csv",
        default="",
        help="Optional CSV of supporting page updates to append (no defaults). Columns: cluster_id,bucket_candidate,primary_target_page,primary_target_url,recommended_cta,notes",
    )
    args = ap.parse_args()

    rows = read_csv(args.input)
    fetched_at = datetime.now(timezone.utc).isoformat()

    clusters: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in rows:
        if (r.get("status") or "").strip().lower() == "cancelled":
            continue
        clusters[cluster_key(r)].append(r)

    out: List[Dict[str, object]] = []
    for cid, items in sorted(clusters.items(), key=lambda kv: kv[0]):
        # summarize keywords
        kw_stats: List[Tuple[str, int, float]] = []
        for it in items:
            kw = (it.get("query") or "").strip()
            impr = to_int(it.get("impressions", ""))
            pos = to_float(it.get("position", ""))
            kw_stats.append((kw, impr, pos))

        primary_kw = choose_primary_keyword(kw_stats)
        supporting = [k for k, _, _ in kw_stats if k and k != primary_kw]
        supporting = supporting[:12]

        primary_url = (items[0].get("primary_target_url") or "").strip()
        primary_page = (items[0].get("primary_target_page") or "").strip()

        # Override target for post clusters
        if cid.startswith("post::"):
            primary_page = "New blog post"
            primary_url = "(new)"

        total_impr = sum(impr for _, impr, _ in kw_stats)
        best_pos = min((pos for _, _, pos in kw_stats if pos > 0), default=0.0)

        out.append(
            {
                "month": args.month,
                "cluster_id": cid,
                "bucket_candidate": bucket_candidate_for_cluster(cid),
                "primary_target_page": primary_page,
                "primary_target_url": primary_url,
                "primary_keyword": primary_kw,
                "supporting_keywords": " | ".join(supporting),
                "keywords_count": len([k for k, _, _ in kw_stats if k]),
                "total_impressions": total_impr,
                "best_position": best_pos,
                "recommended_cta": lead_cta_for_cluster(cid),
                "notes": (
                    "Cluster derived from Semrush non-brand opportunities + cannibalization. "
                    "Pending DataForSEO enrichment for volume/SERP format and final selection."
                ),
                "status": "candidate",
                "fetched_at": fetched_at,
            }
        )

    # Optional supporting-page updates (client-specific; keep out of template defaults)
    if args.support_templates_csv:
        support_rows = read_csv(args.support_templates_csv)
        for r in support_rows:
            out.append(
                {
                    "month": args.month,
                    "cluster_id": (r.get("cluster_id") or "").strip(),
                    "bucket_candidate": (r.get("bucket_candidate") or "Bucket_C_SupportingPages").strip(),
                    "primary_target_page": (r.get("primary_target_page") or "").strip(),
                    "primary_target_url": (r.get("primary_target_url") or "").strip(),
                    "primary_keyword": "",
                    "supporting_keywords": "",
                    "keywords_count": 0,
                    "total_impressions": 0,
                    "best_position": 0.0,
                    "recommended_cta": (r.get("recommended_cta") or "").strip(),
                    "notes": (r.get("notes") or "").strip(),
                    "status": "candidate",
                    "fetched_at": fetched_at,
                }
            )

    write_csv(
        args.output,
        [
            "month",
            "cluster_id",
            "bucket_candidate",
            "primary_target_page",
            "primary_target_url",
            "primary_keyword",
            "supporting_keywords",
            "keywords_count",
            "total_impressions",
            "best_position",
            "recommended_cta",
            "notes",
            "status",
            "fetched_at",
        ],
        out,
    )
    print(f"Wrote clusters -> {args.output} ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

