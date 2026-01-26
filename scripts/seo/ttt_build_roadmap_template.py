#!/usr/bin/env python3
"""
Generate a first-pass yearly roadmap + first-wave content shortlist.

Inputs (generated earlier in this workflow):
  - work/seo/plan/{client}_keywords_cluster_candidates.csv

Outputs (CSV) under work/seo/plan/ (git-ignored):
  - {client}_{year}_roadmap.csv
  - {client}_{year}_content_ideas_first_wave.csv

This is intentionally a *template generator*: it uses real DataForSEO-derived
cluster candidates, but leaves room for human review (final topics, URLs, links).
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def _read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] if s else ""


def _clean_client_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a yearly roadmap template + first-wave content ideas.")
    ap.add_argument("--client-key", default="client", help="Prefix for default input/output file paths")
    ap.add_argument("--clusters-csv", default="", help="Override default clusters CSV path")
    ap.add_argument("--output-dir", default="work/seo/plan")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--first-wave-count", type=int, default=5)
    args = ap.parse_args()

    client_key = _clean_client_key(args.client_key)
    if not args.clusters_csv:
        args.clusters_csv = os.path.join(args.output_dir, f"{client_key}_keywords_cluster_candidates.csv")

    clusters = _read_csv(args.clusters_csv)
    clusters = [c for c in clusters if (c.get("primary_keyword") or "").strip()]
    if not clusters:
        raise SystemExit("No clusters found. Generate keyword cluster candidates first.")

    fetched_at = datetime.now(timezone.utc).isoformat()

    # First wave content ideas: top N clusters
    n = max(1, int(args.first_wave_count))
    first_wave = clusters[:n]
    ideas_rows: List[Dict[str, object]] = []
    for i, c in enumerate(first_wave, start=1):
        primary = (c.get("primary_keyword") or "").strip()
        cluster_key = (c.get("cluster_key") or "").strip()
        ideas_rows.append(
            {
                "priority": i,
                "cluster_key": cluster_key,
                "primary_keyword": primary,
                "suggested_content_type": "guide",
                "suggested_slug": _slugify(primary),
                "internal_link_hub_candidate": "TBD",
                "notes": "Generated from DataForSEO-derived cluster candidates; finalize after SERP review + brand constraints.",
                "fetched_at": fetched_at,
            }
        )

    out_ideas = os.path.join(args.output_dir, f"{client_key}_{args.year}_content_ideas_first_wave.csv")
    _write_csv(
        out_ideas,
        [
            "priority",
            "cluster_key",
            "primary_keyword",
            "suggested_content_type",
            "suggested_slug",
            "internal_link_hub_candidate",
            "notes",
            "fetched_at",
        ],
        ideas_rows,
    )

    # 12-month roadmap skeleton: assign clusters in order, repeating if needed.
    months = [
        ("01", "Baseline + foundational content"),
        ("02", "Category/solution pages + internal linking"),
        ("03", "Comparisons + buying intent"),
        ("04", "How-to + safety/compliance"),
        ("05", "Problem/solution (pain) content"),
        ("06", "Refresh + consolidate (cannibalization prevention)"),
        ("07", "Peak-season topics (if applicable)"),
        ("08", "Video/visual support + FAQs (draft-first)"),
        ("09", "Backlink campaign month (gap-driven)"),
        ("10", "Programmatic refresh + new clusters"),
        ("11", "Year-end measurement + cleanup"),
        ("12", "Plan next year + evergreen refresh"),
    ]

    roadmap_rows: List[Dict[str, object]] = []
    for idx, (mm, theme) in enumerate(months):
        c = clusters[idx % len(clusters)]
        primary = (c.get("primary_keyword") or "").strip()
        cluster_key = (c.get("cluster_key") or "").strip()
        roadmap_rows.append(
            {
                "month": f"{args.year}-{mm}",
                "theme": theme,
                "cluster_key": cluster_key,
                "primary_keyword": primary,
                "content_piece_title": "TBD",
                "content_type": "post_or_page",
                "planned_slug": _slugify(primary),
                "internal_links_from": "TBD",
                "internal_links_to": "TBD",
                "backlink_targets": "TBD",
                "status": "draft_plan",
                "notes": "Template row. Replace placeholders after SERP + backlink review and once GSC/GA4 baseline arrives.",
                "fetched_at": fetched_at,
            }
        )

    out_roadmap = os.path.join(args.output_dir, f"{client_key}_{args.year}_roadmap.csv")
    _write_csv(
        out_roadmap,
        [
            "month",
            "theme",
            "cluster_key",
            "primary_keyword",
            "content_piece_title",
            "content_type",
            "planned_slug",
            "internal_links_from",
            "internal_links_to",
            "backlink_targets",
            "status",
            "notes",
            "fetched_at",
        ],
        roadmap_rows,
    )

    print("OK")
    print("wrote:", out_ideas)
    print("wrote:", out_roadmap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

