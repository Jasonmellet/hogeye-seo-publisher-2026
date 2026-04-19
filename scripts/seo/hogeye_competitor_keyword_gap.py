#!/usr/bin/env python3
"""
Competitor keyword gap analysis for HogEye.

For each competitor domain, pulls keywords_for_site via DataForSEO Google Ads API,
then cross-references against HogEye's keyword universe to find what competitors
rank for that HogEye doesn't appear for.

Competitors (hardcoded defaults for HogEye, override with --competitors):
  jagerpro.com, gamechangertraps.com, pigbrig.com

Inputs:
  - work/seo/plan/hogeye_keywords_for_site.csv   (from ttt_build_keyword_universe.py)
    Falls back to seed keywords CSV if universe not yet built.

Outputs (in --output-dir, default work/seo/plan/):
  - hogeye_competitor_kws_{domain}.csv     per-competitor keyword list with volumes
  - hogeye_keyword_gap_combined.csv        all gap keywords ranked by competitor count + volume
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"

DEFAULT_COMPETITORS = [
    "jagerpro.com",
    "gamechangertraps.com",
    "pigbrig.com",
]

# Terms that indicate a keyword is off-strategy for HogEye — skip even if it's a gap
BLACKLIST_FRAGMENTS = [
    "security camera",
    "driveway camera",
    "theft",
    "burglary",
    "doorbell",
    "nanny cam",
    "spy cam",
    "trail camera deer",
    "deer cam",
    "hunting camera",
    "game camera deer",
    "motion detector light",
]


def _clean_domain(d: str) -> str:
    d = (d or "").strip().lower()
    if d.startswith("www."):
        d = d[4:]
    return d


def _clean_client_key(s: str) -> str:
    s = re.sub(r"[^a-z0-9_-]+", "_", (s or "").strip().lower())
    return re.sub(r"_+", "_", s).strip("_") or "client"


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


def _is_blacklisted(keyword: str) -> bool:
    kl = keyword.lower()
    return any(frag in kl for frag in BLACKLIST_FRAGMENTS)


def _dfs_keywords_for_site(
    *,
    login: str,
    password: str,
    domain: str,
    location_code: int,
    language_code: str,
    limit: int = 1000,
) -> List[dict]:
    url = f"{API_BASE}/keywords_data/google_ads/keywords_for_site/live"
    body = [
        {
            "target": domain,
            "target_type": "site",
            "location_code": location_code,
            "language_code": language_code,
        }
    ]
    r = requests.post(url, json=body, auth=(login, password), timeout=120)
    r.raise_for_status()
    data = r.json()
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    results = tasks[0].get("result") or []
    return results[:limit]


def main() -> int:
    ap = argparse.ArgumentParser(description="Competitor keyword gap analysis for HogEye.")
    ap.add_argument("--project-root", default=str(Path.cwd()))
    ap.add_argument(
        "--competitors",
        default=",".join(DEFAULT_COMPETITORS),
        help="Comma-separated competitor domains (default: jagerpro.com,gamechangertraps.com,pigbrig.com)",
    )
    ap.add_argument(
        "--target-domain",
        default="",
        help="HogEye domain (defaults to WP_SITE_URL host)",
    )
    ap.add_argument(
        "--hogeye-universe-csv",
        default="",
        help="Path to HogEye keyword universe CSV (defaults to work/seo/plan/hogeye_keywords_for_site.csv)",
    )
    ap.add_argument(
        "--seed-csv",
        default="work/seo/plan/hogeye_may_seed_keywords.csv",
        help="Fallback seed keywords CSV if universe not yet built",
    )
    ap.add_argument("--output-dir", default="work/seo/plan")
    ap.add_argument("--min-volume", type=int, default=0, help="Minimum monthly search volume to include (0 = include all)")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in .env")

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en") or "en").strip()

    target_domain = _clean_domain(
        args.target_domain or (urlparse((os.environ.get("WP_SITE_URL") or "").strip()).hostname or "")
    )
    if not target_domain:
        raise SystemExit("Missing --target-domain and could not infer from WP_SITE_URL.")

    competitors = [_clean_domain(c) for c in args.competitors.split(",") if c.strip()]
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Load HogEye's existing keyword universe (to find what we already cover)
    universe_path = args.hogeye_universe_csv or os.path.join(args.output_dir, "hogeye_keywords_for_site.csv")
    hogeye_keywords: Set[str] = set()
    if os.path.isfile(universe_path):
        for row in _read_csv(universe_path):
            kw = (row.get("keyword") or "").strip().lower()
            if kw:
                hogeye_keywords.add(kw)
        print(f"Loaded {len(hogeye_keywords)} HogEye universe keywords from {universe_path}")
    else:
        # Fall back to seed keywords as a rough proxy
        seed_path = args.seed_csv
        if os.path.isfile(seed_path):
            for row in _read_csv(seed_path):
                kw = (row.get("keyword") or "").strip().lower()
                if kw:
                    hogeye_keywords.add(kw)
            print(f"Universe CSV not found — using {len(hogeye_keywords)} seed keywords as proxy from {seed_path}")
        else:
            print("Warning: no HogEye keyword universe found. All competitor keywords will be treated as gaps.")

    # Pull keywords for each competitor
    # gap_map: keyword -> {volume, competitors_with_kw, competition}
    gap_map: Dict[str, Dict] = defaultdict(lambda: {"search_volume": 0, "competitors": [], "competition": ""})
    all_comp_rows: List[Dict[str, object]] = []

    for comp in competitors:
        print(f"\nFetching keywords for competitor: {comp} ...")
        results = _dfs_keywords_for_site(
            login=login,
            password=password,
            domain=comp,
            location_code=location_code,
            language_code=language_code,
        )
        print(f"  → {len(results)} keywords returned")

        comp_rows: List[Dict[str, object]] = []
        for r in results:
            kw = (r.get("keyword") or "").strip()
            if not kw or _is_blacklisted(kw):
                continue
            vol = r.get("search_volume") or 0
            try:
                vol = int(vol)
            except Exception:
                vol = 0
            if args.min_volume and vol < args.min_volume:
                continue

            comp_rows.append({
                "competitor_domain": comp,
                "keyword": kw,
                "search_volume": vol,
                "cpc": r.get("cpc") or "",
                "competition": r.get("competition") or "",
                "competition_index": r.get("competition_index") or "",
                "in_hogeye_universe": "yes" if kw.lower() in hogeye_keywords else "no",
                "location_code": location_code,
                "language_code": language_code,
                "fetched_at": fetched_at,
            })

            # Track for gap analysis
            kl = kw.lower()
            if kl not in hogeye_keywords:
                if vol > gap_map[kl]["search_volume"]:
                    gap_map[kl]["search_volume"] = vol
                    gap_map[kl]["competition"] = r.get("competition") or ""
                    gap_map[kl]["cpc"] = r.get("cpc") or ""
                    gap_map[kl]["keyword_display"] = kw  # preserve original casing
                if comp not in gap_map[kl]["competitors"]:
                    gap_map[kl]["competitors"].append(comp)

        all_comp_rows.extend(comp_rows)

        # Write per-competitor file
        safe_domain = re.sub(r"[^a-z0-9_-]", "_", comp)
        out_comp = os.path.join(args.output_dir, f"hogeye_competitor_kws_{safe_domain}.csv")
        _write_csv(
            out_comp,
            ["competitor_domain", "keyword", "search_volume", "cpc", "competition",
             "competition_index", "in_hogeye_universe", "location_code", "language_code", "fetched_at"],
            comp_rows,
        )
        print(f"  wrote: {out_comp} ({len(comp_rows)} rows)")

    # Write combined gap file — sorted by competitor_count DESC, then volume DESC
    gap_rows: List[Dict[str, object]] = []
    for kl, data in gap_map.items():
        gap_rows.append({
            "keyword": data.get("keyword_display", kl),
            "competitor_count": len(data["competitors"]),
            "competitors": ", ".join(data["competitors"]),
            "search_volume": data["search_volume"],
            "cpc": data.get("cpc", ""),
            "competition": data["competition"],
            "target_domain": target_domain,
            "in_hogeye_universe": "no",
            "location_code": location_code,
            "language_code": language_code,
            "fetched_at": fetched_at,
        })
    gap_rows.sort(key=lambda r: (-int(r["competitor_count"]), -int(r["search_volume"] or 0)))

    out_gap = os.path.join(args.output_dir, "hogeye_keyword_gap_combined.csv")
    _write_csv(
        out_gap,
        ["keyword", "competitor_count", "competitors", "search_volume", "cpc", "competition",
         "target_domain", "in_hogeye_universe", "location_code", "language_code", "fetched_at"],
        gap_rows,
    )

    print(f"\n{'='*60}")
    print(f"Gap keywords found: {len(gap_rows)}")
    print(f"Wrote combined gap file: {out_gap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
