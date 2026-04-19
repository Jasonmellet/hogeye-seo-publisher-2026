#!/usr/bin/env python3
"""
Enrich Feb 2026 cluster candidates with DataForSEO keyword metrics.

Reads:
  - work/seo/plan/Feb_2026_clusters_candidates.csv

Writes:
  - work/seo/plan/Feb_2026_clusters_enriched.csv

Auth:
  - Reads DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD from environment
  - Loads .env from project root if present (gitignored in this repo)

Default geo/language:
  - DATAFORSEO_LOCATION_CODE=2840
  - DATAFORSEO_LANGUAGE_CODE=en

Note:
  - This script does NOT change any WordPress content.
  - It only produces spreadsheet-ready enrichment data.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


API_BASE = "https://api.dataforseo.com/v3"


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


def split_keywords(primary: str, supporting: str, limit_supporting: int = 10) -> List[str]:
    kws: List[str] = []
    p = (primary or "").strip()
    if p:
        kws.append(p)
    supp = [s.strip() for s in (supporting or "").split("|") if s.strip()]
    kws.extend(supp[: max(0, limit_supporting)])
    # Deduplicate while preserving order
    seen = set()
    out = []
    for k in kws:
        kl = k.lower()
        if kl in seen:
            continue
        seen.add(kl)
        out.append(k)
    return out


def chunks(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def dfs_search_volume_live(
    *,
    login: str,
    password: str,
    keywords: List[str],
    location_code: int,
    language_code: str,
) -> Dict[str, Dict[str, object]]:
    """
    Calls DataForSEO Keywords Data API Search Volume (live).

    Returns a mapping: keyword_lower -> metrics dict
    """
    url = f"{API_BASE}/keywords_data/google_ads/search_volume/live"
    body = [
        {
            "location_code": location_code,
            "language_code": language_code,
            "keywords": keywords,
        }
    ]
    r = requests.post(url, json=body, auth=(login, password), timeout=60)
    r.raise_for_status()
    data = r.json()
    out: Dict[str, Dict[str, object]] = {}

    tasks = data.get("tasks") or []
    if not tasks:
        return out
    results = (tasks[0].get("result") or [])
    if not results:
        return out

    # DataForSEO can return either:
    # - result[0].items (legacy/alternate shape), OR
    # - result as a list of per-keyword metric objects (common for search_volume/live).
    #
    # We support both shapes to keep the pipeline resilient.

    # Shape A: per-keyword objects directly in result list
    direct_like = any(isinstance(r, dict) and (r.get("keyword") or r.get("key")) for r in results)
    if direct_like:
        for r0 in results:
            if not isinstance(r0, dict):
                continue
            kw = (r0.get("keyword") or r0.get("key") or "").strip()
            if not kw:
                continue
            out[kw.lower()] = {
                "keyword": kw,
                "search_volume": r0.get("search_volume") or r0.get("keyword_info", {}).get("search_volume"),
                "cpc": r0.get("cpc") or r0.get("keyword_info", {}).get("cpc"),
                "competition": r0.get("competition") or r0.get("keyword_info", {}).get("competition"),
                "competition_level": r0.get("competition_level") or r0.get("keyword_info", {}).get("competition_level"),
            }
        return out

    # Shape B: result[0].items
    items = (results[0].get("items") or results[0].get("keywords") or [])
    if isinstance(items, dict):
        items = list(items.values())

    for it in items:
        kw = (it.get("keyword") or it.get("key") or "").strip()
        if not kw:
            continue
        out[kw.lower()] = {
            "keyword": kw,
            "search_volume": it.get("search_volume") or it.get("keyword_info", {}).get("search_volume"),
            "cpc": it.get("cpc") or it.get("keyword_info", {}).get("cpc"),
            "competition": it.get("competition") or it.get("keyword_info", {}).get("competition"),
            "competition_level": it.get("competition_level") or it.get("keyword_info", {}).get("competition_level"),
        }
    return out


def to_float(v: object) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def to_int(v: object) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Enrich Feb 2026 clusters with DataForSEO keyword metrics.")
    ap.add_argument(
        "--input",
        default="work/seo/plan/Feb_2026_clusters_candidates.csv",
        help="Path to Feb_2026_clusters_candidates.csv",
    )
    ap.add_argument(
        "--output",
        default="work/seo/plan/Feb_2026_clusters_enriched.csv",
        help="Path to write Feb_2026_clusters_enriched.csv",
    )
    ap.add_argument(
        "--project-root",
        default=str(Path.cwd()),
        help="Project root (to load .env)",
    )
    ap.add_argument("--batch-size", type=int, default=100, help="Keywords per API call")
    ap.add_argument("--supporting-limit", type=int, default=10, help="Supporting keywords per cluster to enrich")
    args = ap.parse_args()

    # Load .env (gitignored) if present
    load_dotenv(os.path.join(args.project_root, ".env"), override=False)

    login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
    password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD. Add them to .env (gitignored) or export them.")

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en").strip() or "en"

    clusters = read_csv(args.input)
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Collect all keywords we need to enrich
    cluster_keywords: Dict[str, List[str]] = {}
    all_keywords: List[str] = []
    for r in clusters:
        if (r.get("status") or "").strip().lower() != "candidate":
            continue
        cid = (r.get("cluster_id") or "").strip()
        kws = split_keywords(r.get("primary_keyword", ""), r.get("supporting_keywords", ""), limit_supporting=args.supporting_limit)
        if not cid or not kws:
            continue
        cluster_keywords[cid] = kws
        all_keywords.extend(kws)

    # Deduplicate all keywords
    seen = set()
    dedup_all = []
    for k in all_keywords:
        kl = k.lower()
        if kl in seen:
            continue
        seen.add(kl)
        dedup_all.append(k)

    metrics_map: Dict[str, Dict[str, object]] = {}
    for kw_batch in chunks(dedup_all, max(1, args.batch_size)):
        batch_map = dfs_search_volume_live(
            login=login,
            password=password,
            keywords=kw_batch,
            location_code=location_code,
            language_code=language_code,
        )
        metrics_map.update(batch_map)

    enriched_rows: List[Dict[str, object]] = []
    for r in clusters:
        cid = (r.get("cluster_id") or "").strip()
        kws = cluster_keywords.get(cid, [])
        if not kws:
            # still include row, but without metrics
            enriched_rows.append({**r, "dfs_location_code": location_code, "dfs_language_code": language_code, "dfs_enriched_at": fetched_at})
            continue

        primary_kw = (r.get("primary_keyword") or "").strip()
        primary_metrics = metrics_map.get(primary_kw.lower(), {}) if primary_kw else {}

        # Aggregate supporting metrics
        volumes: List[int] = []
        cpcs: List[float] = []
        comps: List[float] = []
        covered = 0
        for k in kws:
            m = metrics_map.get(k.lower())
            if not m:
                continue
            covered += 1
            sv = to_int(m.get("search_volume"))
            if sv is not None:
                volumes.append(sv)
            cpc = to_float(m.get("cpc"))
            if cpc is not None:
                cpcs.append(cpc)
            comp = to_float(m.get("competition"))
            if comp is not None:
                comps.append(comp)

        enriched_rows.append(
            {
                **r,
                "dfs_location_code": location_code,
                "dfs_language_code": language_code,
                "dfs_keywords_requested": len(kws),
                "dfs_keywords_covered": covered,
                "dfs_primary_search_volume": to_int(primary_metrics.get("search_volume")),
                "dfs_primary_cpc": to_float(primary_metrics.get("cpc")),
                "dfs_primary_competition": to_float(primary_metrics.get("competition")),
                "dfs_primary_competition_level": primary_metrics.get("competition_level"),
                "dfs_cluster_search_volume_sum": sum(volumes) if volumes else None,
                "dfs_cluster_search_volume_max": max(volumes) if volumes else None,
                "dfs_cluster_cpc_avg": (sum(cpcs) / len(cpcs)) if cpcs else None,
                "dfs_cluster_competition_avg": (sum(comps) / len(comps)) if comps else None,
                "dfs_enriched_at": fetched_at,
            }
        )

    # Fieldnames = input + new columns (stable order)
    base_fields = list(clusters[0].keys()) if clusters else []
    extra_fields = [
        "dfs_location_code",
        "dfs_language_code",
        "dfs_keywords_requested",
        "dfs_keywords_covered",
        "dfs_primary_search_volume",
        "dfs_primary_cpc",
        "dfs_primary_competition",
        "dfs_primary_competition_level",
        "dfs_cluster_search_volume_sum",
        "dfs_cluster_search_volume_max",
        "dfs_cluster_cpc_avg",
        "dfs_cluster_competition_avg",
        "dfs_enriched_at",
    ]
    fieldnames = base_fields + [f for f in extra_fields if f not in base_fields]

    write_csv(args.output, fieldnames, enriched_rows)
    print(f"Wrote DataForSEO enrichment -> {args.output} ({len(enriched_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

