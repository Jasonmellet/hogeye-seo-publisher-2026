#!/usr/bin/env python3
"""
Build a spreadsheet-ready Feb 2026 draft plan from Semrush OTI exports.

Inputs:
  - opportunities_nonbrand.csv (from normalize_semrush_oti.py + nonbrand filter)
  - cannibalization_nonbrand.csv (from find_semrush_cannibalization.py)

Output:
  - plan_feb_2026_draft.csv: one row per "action" (update or new content)

This intentionally stays simple (KISS):
  - Uses a small set of keyword "themes" to route queries to a primary target page.
  - Produces a reviewable plan BEFORE any site text changes.
"""

from __future__ import annotations

import argparse
import csv
import os
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


def to_int(v: str) -> Optional[int]:
    s = (v or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def to_float(v: str) -> Optional[float]:
    s = (v or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def pick_theme(query: str) -> str:
    q = (query or "").lower()
    # Order matters: more specific first.
    # Normalize common separators
    q = q.replace("+", " ")
    if "coed" in q:
        return "coed_sleepaway"
    if "for teens" in q or "teen" in q:
        return "sleepaway_teens"
    if "for kids" in q:
        return "sleepaway_kids"
    if "near me" in q:
        return "near_me"
    if "sleepaway" in q:
        if "upstate" in q:
            return "sleepaway_upstate_ny"
        if "new york" in q or " ny" in q or q.endswith("ny"):
            return "sleepaway_ny"
        return "sleepaway_generic"
    if "summer camp" in q or "summer camps" in q:
        if "upstate" in q:
            return "summer_camp_upstate_ny"
        if "new york" in q or " ny" in q or q.endswith("ny"):
            return "summer_camp_ny"
        return "summer_camp_generic"
    if "upstate" in q:
        return "upstate_ny_other"
    if "new york" in q or " ny" in q or q.endswith("ny"):
        return "ny_other"
    return "other"


def primary_target_for_theme(theme: str) -> Tuple[str, str]:
    """
    Returns (primary_url, primary_page_name)

    User decisions already made:
      - Homepage is primary for "summer camps in new york" cluster
      - Sleepaway hub should be a dedicated page (we recommend repurposing /upstate-ny-camp/)
    """
    raise RuntimeError("primary_target_for_theme() must be configured via CLI in this template repo.")

    # User decision: homepage is primary for summer-camp NY head terms
    if theme in ("summer_camp_ny", "summer_camp_upstate_ny", "summer_camp_generic"):
        return homepage
    # Sleepaway intent should route to a dedicated hub page (not the homepage)
    if theme in (
        "sleepaway_ny",
        "sleepaway_upstate_ny",
        "sleepaway_generic",
        "sleepaway_teens",
        "sleepaway_kids",
        "near_me",
        "coed_sleepaway",
    ):
        # Keep sleepaway intent off the homepage; route to hub.
        return sleepaway_hub
    return homepage


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Feb 2026 draft plan from Semrush OTI exports.")
    ap.add_argument("--opportunities", required=True, help="Path to opportunities_nonbrand.csv")
    ap.add_argument("--cannibalization", required=True, help="Path to cannibalization_nonbrand.csv")
    ap.add_argument("--output", required=True, help="Path to write plan_feb_2026_draft.csv")
    ap.add_argument("--top", type=int, default=60, help="How many opportunity rows to consider")
    ap.add_argument("--homepage-url", default=os.environ.get("HOMEPAGE_URL", ""), help="Homepage URL (e.g. https://example.com/)")
    ap.add_argument("--sleepaway-hub-url", default=os.environ.get("SLEEPAWAY_HUB_URL", ""), help="Sleepaway hub URL (client-specific)")
    args = ap.parse_args()

    fetched_at = datetime.now(timezone.utc).isoformat()

    opp = read_csv(args.opportunities)[: max(0, args.top)]
    cann = read_csv(args.cannibalization)
    cann_map = { (r.get("query") or "").strip().lower(): r for r in cann if (r.get("query") or "").strip() }

    rows: List[Dict[str, object]] = []
    seen_actions = set()

    for r in opp:
        query = (r.get("query") or "").strip()
        if not query:
            continue
        theme = pick_theme(query)
        homepage_url = (args.homepage_url or "").strip()
        hub_url = (args.sleepaway_hub_url or "").strip()
        if not homepage_url or not hub_url:
            raise SystemExit(
                "Missing homepage/hub routing.\n"
                "- Pass --homepage-url and --sleepaway-hub-url, or\n"
                "- Set HOMEPAGE_URL and SLEEPAWAY_HUB_URL in your environment."
            )
        # Normalize (no trailing slash except homepage)
        homepage_url = homepage_url.rstrip("/") + "/"
        hub_url = hub_url.rstrip("/")

        # User decision: homepage is primary for summer-camp head terms; sleepaway intent routes to hub.
        if theme in ("summer_camp_ny", "summer_camp_upstate_ny", "summer_camp_generic"):
            primary_url, primary_page = (homepage_url, "Homepage")
        elif theme in (
            "sleepaway_ny",
            "sleepaway_upstate_ny",
            "sleepaway_generic",
            "sleepaway_teens",
            "sleepaway_kids",
            "near_me",
            "coed_sleepaway",
        ):
            primary_url, primary_page = (hub_url, "Sleepaway hub")
        else:
            primary_url, primary_page = (homepage_url, "Homepage")

        impressions = to_int(r.get("impressions", ""))
        position = to_float(r.get("position", ""))
        ctr = to_float(r.get("ctr_pct", ""))
        opp_score = to_float(r.get("opportunity_score", ""))

        # If cannibalized, show all competing URLs and recommended primary.
        cann_row = cann_map.get(query.lower())
        competing_urls = (cann_row.get("urls") if cann_row else "") if cann_row else ""

        # Action key: primary_url + query (so we don't duplicate).
        action_key = f"{primary_url}::{query.lower()}"
        if action_key in seen_actions:
            continue
        seen_actions.add(action_key)

        # Decide action type:
        # - If query is already associated with the chosen primary_url in opp data, it's a page update.
        # - Otherwise still keep as "update" for now; a later step can decide net-new posts after sitemap join.
        current_best_url = (r.get("url_canonical") or "").strip()
        action_type = "update_existing_page" if current_best_url == primary_url else "resolve_cannibalization"

        rows.append(
            {
                "month": "2026-02",
                "theme": theme,
                "primary_target_page": primary_page,
                "primary_target_url": primary_url,
                "query": query,
                "impressions": impressions,
                "position": position,
                "ctr_pct": ctr,
                "opportunity_score": opp_score,
                "current_url_from_report": current_best_url,
                "competing_urls_if_any": competing_urls,
                "recommended_action_type": action_type,
                "recommended_actions_notes": (
                    "Build/strengthen topical coverage for this query on the primary page. "
                    "Add internal links from competing pages with aligned anchor text; reduce conflicting H1/title intent on competing pages."
                ),
                "status": "draft",
                "fetched_at": fetched_at,
            }
        )

    write_csv(
        args.output,
        [
            "month",
            "theme",
            "primary_target_page",
            "primary_target_url",
            "query",
            "impressions",
            "position",
            "ctr_pct",
            "opportunity_score",
            "current_url_from_report",
            "competing_urls_if_any",
            "recommended_action_type",
            "recommended_actions_notes",
            "status",
            "fetched_at",
        ],
        rows,
    )

    print(f"Plan rows: {len(rows)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

