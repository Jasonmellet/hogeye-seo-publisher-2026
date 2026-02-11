#!/usr/bin/env python3
"""
HogEye: trap-release keyword analysis (DataForSEO + optional GSC).

Legacy filename note:
- This file keeps its old name for backward compatibility.
- Preferred entry point: scripts/seo/hogeye_trap_release_keyword_analysis.py

Goal:
- Validate keyword demand for trap monitoring and remote trap closure terminology.

What it does:
1) Generates ~10 seed keyword variations (overrideable)
2) Optionally expands seeds via DataForSEO keywords_for_keywords/live
3) Calls DataForSEO Keywords Data API search_volume/live for the final keyword set
4) Optionally calls GSC Search Analytics for exact-match query stats (top keywords only)
5) Writes a small report bundle under work/seo/hogeye/keyword_analysis/

Safety:
- Read-only (no WordPress writes)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _utc_now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def _ymd(d: date) -> str:
    return d.isoformat()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _dedupe(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in seq:
        k = (s or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append((s or "").strip())
    return out


def _chunks(seq: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), max(1, size)):
        yield seq[i : i + max(1, size)]


def default_seed_variations() -> List[str]:
    # 10-ish deliberate trap-operation variants.
    return [
        "wild hog trap release camera system",
        "hog trap camera with remote trigger",
        "remote trap monitoring and closure",
        "trap gate trigger camera",
        "sounder capture timing",
        "hog trap camera",
        "remote hog trap trigger",
        "hog trap closure timing",
        "trap monitoring system for wild hogs",
        "low latency trap trigger",
    ]


def _dfs_post(login: str, password: str, path: str, payload: list[dict], timeout: int = 90) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.post(url, json=payload, auth=(login, password), timeout=timeout)
    r.raise_for_status()
    return r.json()


def dfs_keywords_for_keywords_live(
    *,
    login: str,
    password: str,
    keywords: List[str],
    location_code: int,
    language_code: str,
    sort_by: str,
) -> List[Dict[str, Any]]:
    """
    DataForSEO Keywords Data API keywords_for_keywords/live.

    Returns a list of item dicts. Item shapes vary slightly across API versions,
    so downstream parsing should be defensive.
    """
    data = _dfs_post(
        login,
        password,
        "/keywords_data/google_ads/keywords_for_keywords/live",
        [
            {
                "keywords": keywords,
                "location_code": location_code,
                "language_code": language_code,
                "sort_by": sort_by,
            }
        ],
        timeout=120,
    )
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    res = tasks[0].get("result") or []
    if not res:
        return []

    # Common shapes:
    # - result[0].items: list of keyword items
    # - result already is a list of keyword items
    if isinstance(res, list) and any(isinstance(x, dict) and ("keyword" in x or "key" in x) for x in res):
        return [x for x in res if isinstance(x, dict)]

    r0 = res[0] if isinstance(res, list) and res else {}
    items = (r0.get("items") or r0.get("keywords") or [])
    if isinstance(items, dict):
        items = list(items.values())
    return [x for x in items if isinstance(x, dict)]


def dfs_search_volume_live(
    *,
    login: str,
    password: str,
    keywords: List[str],
    location_code: int,
    language_code: str,
) -> Dict[str, Dict[str, Any]]:
    """
    DataForSEO Keywords Data API Search Volume (live).
    Returns mapping keyword_lower -> metrics dict.
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
    out: Dict[str, Dict[str, Any]] = {}

    tasks = data.get("tasks") or []
    if not tasks:
        return out
    results = (tasks[0].get("result") or [])
    if not results:
        return out

    direct_like = any(isinstance(r0, dict) and (r0.get("keyword") or r0.get("key")) for r0 in results)
    if direct_like:
        for r0 in results:
            if not isinstance(r0, dict):
                continue
            kw = (r0.get("keyword") or r0.get("key") or "").strip()
            if not kw:
                continue
            ki = r0.get("keyword_info") if isinstance(r0.get("keyword_info"), dict) else {}
            out[kw.lower()] = {
                "keyword": kw,
                "search_volume": r0.get("search_volume") or ki.get("search_volume"),
                "cpc": r0.get("cpc") or ki.get("cpc"),
                "competition": r0.get("competition") or ki.get("competition"),
                "competition_level": r0.get("competition_level") or ki.get("competition_level"),
            }
        return out

    items = (results[0].get("items") or results[0].get("keywords") or [])
    if isinstance(items, dict):
        items = list(items.values())
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        kw = (it.get("keyword") or it.get("key") or "").strip()
        if not kw:
            continue
        ki = it.get("keyword_info") if isinstance(it.get("keyword_info"), dict) else {}
        out[kw.lower()] = {
            "keyword": kw,
            "search_volume": it.get("search_volume") or ki.get("search_volume"),
            "cpc": it.get("cpc") or ki.get("cpc"),
            "competition": it.get("competition") or ki.get("competition"),
            "competition_level": it.get("competition_level") or ki.get("competition_level"),
        }
    return out


def _is_relevant_candidate(keyword: str) -> bool:
    """
    Keep expansion tight to trap monitoring/closure intent.
    """
    k = (keyword or "").lower()
    tokens = [
        "camera",
        "cameras",
        "remote",
        "trigger",
        "release",
        "closure",
        "close",
        "trap",
        "gate",
        "hog",
        "sounder",
        "baiting",
        "conditioning",
        "monitor",
        "monitoring",
    ]
    return any(t in k for t in tokens)


def _extract_metrics_from_keywords_for_keywords_item(it: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort normalize metrics that may come back on keywords_for_keywords items.
    """
    kw = (it.get("keyword") or it.get("key") or "").strip()
    ki = it.get("keyword_info") if isinstance(it.get("keyword_info"), dict) else {}
    return {
        "keyword": kw,
        "search_volume": it.get("search_volume") or ki.get("search_volume"),
        "cpc": it.get("cpc") or ki.get("cpc"),
        "competition": it.get("competition") or ki.get("competition"),
        "competition_level": it.get("competition_level") or ki.get("competition_level"),
        "competition_index": it.get("competition_index") or ki.get("competition_index"),
    }


@dataclass(frozen=True)
class GscQueryStat:
    keyword: str
    clicks: float
    impressions: float
    ctr: float
    avg_position: float


def _maybe_build_gsc_service(service_account_json: str):
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception:
        return None
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    creds = service_account.Credentials.from_service_account_file(service_account_json, scopes=scopes)
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def gsc_exact_query_stats(
    *,
    svc,
    site_url: str,
    start_date: date,
    end_date: date,
    keyword: str,
) -> Optional[GscQueryStat]:
    # Exact match query filter. If keyword has no rows, returns None.
    resp = (
        svc.searchanalytics()
        .query(
            siteUrl=site_url,
            body={
                "startDate": _ymd(start_date),
                "endDate": _ymd(end_date),
                "dimensions": ["query"],
                "rowLimit": 1,
                "dimensionFilterGroups": [
                    {
                        "filters": [
                            {"dimension": "query", "operator": "equals", "expression": keyword},
                        ]
                    }
                ],
            },
        )
        .execute()
    )
    rows = resp.get("rows", []) or []
    if not rows:
        return None
    r0 = rows[0]
    return GscQueryStat(
        keyword=keyword,
        clicks=float(r0.get("clicks") or 0.0),
        impressions=float(r0.get("impressions") or 0.0),
        ctr=float(r0.get("ctr") or 0.0),
        avg_position=float(r0.get("position") or 0.0),
    )


def main() -> int:
    load_dotenv(REPO_ROOT / ".env", override=False)

    ap = argparse.ArgumentParser(description="Analyze trap-release keyword demand (DataForSEO + optional GSC).")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (for env parity).")
    ap.add_argument(
        "--keywords",
        default="",
        help="Comma-separated keywords (overrides default seed set).",
    )
    ap.add_argument(
        "--output-dir",
        default="work/seo/hogeye/keyword_analysis",
        help="Base output directory.",
    )
    ap.add_argument("--location-code", type=int, default=0, help="Override DATAFORSEO_LOCATION_CODE")
    ap.add_argument("--language-code", default="", help="Override DATAFORSEO_LANGUAGE_CODE")
    ap.add_argument("--with-gsc", action="store_true", help="Also query GSC for exact-match keyword stats (if configured).")
    ap.add_argument("--gsc-days", type=int, default=365, help="GSC lookback window (default 365).")
    ap.add_argument("--expand", action="store_true", help="Expand seed keywords via DataForSEO keywords_for_keywords/live.")
    ap.add_argument(
        "--expand-sort-by",
        default="search_volume",
        choices=["relevance", "search_volume", "competition_index", "low_top_of_page_bid", "high_top_of_page_bid"],
        help="Sort for DataForSEO keywords_for_keywords/live (default: search_volume).",
    )
    ap.add_argument("--expand-limit", type=int, default=200, help="Max expansion candidates to keep (after filtering).")
    ap.add_argument(
        "--analysis-limit",
        type=int,
        default=50,
        help="How many keywords to fully score (DataForSEO + optional GSC). Default 50.",
    )
    ap.add_argument(
        "--gsc-limit",
        type=int,
        default=50,
        help="How many keywords (max) to query in GSC (exact match). Default 50.",
    )
    args = ap.parse_args()

    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in .env.")

    location_code = args.location_code or int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (args.language_code or os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en")).strip() or "en"

    if args.keywords.strip():
        seeds = _dedupe([k.strip() for k in args.keywords.split(",") if k.strip()])
    else:
        seeds = _dedupe(default_seed_variations())

    expanded_items: List[Dict[str, Any]] = []
    expanded_candidates: List[Dict[str, Any]] = []
    expanded_keywords: List[str] = []

    if args.expand:
        seed_for_expand = seeds[:20]
        expanded_items = dfs_keywords_for_keywords_live(
            login=login,
            password=password,
            keywords=seed_for_expand,
            location_code=location_code,
            language_code=language_code,
            sort_by=str(args.expand_sort_by),
        )

        for it in expanded_items:
            row = _extract_metrics_from_keywords_for_keywords_item(it)
            kw = (row.get("keyword") or "").strip()
            if not kw:
                continue
            if not _is_relevant_candidate(kw):
                continue
            expanded_candidates.append(row)

        # De-dupe, preserve order, then sort by search volume desc.
        seen = set()
        dedup: List[Dict[str, Any]] = []
        for r in expanded_candidates:
            k = (r.get("keyword") or "").strip().lower()
            if not k or k in seen:
                continue
            seen.add(k)
            dedup.append(r)

        def _sv(x: Dict[str, Any]) -> int:
            v = x.get("search_volume")
            try:
                return int(v) if v is not None else 0
            except Exception:
                return 0

        dedup.sort(key=_sv, reverse=True)
        expanded_candidates = dedup[: max(0, int(args.expand_limit))]
        expanded_keywords = [r["keyword"] for r in expanded_candidates if r.get("keyword")]

    run_tag = f"trap_release_{_utc_now_tag()}"
    out_dir = Path(args.output_dir) / run_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    fetched_at = datetime.now(timezone.utc).isoformat()
    merged = _dedupe(seeds + expanded_keywords)

    dfs_map: Dict[str, Dict[str, Any]] = {}
    for batch in _chunks(merged, 100):
        dfs_map.update(
            dfs_search_volume_live(
                login=login,
                password=password,
                keywords=batch,
                location_code=location_code,
                language_code=language_code,
            )
        )

    def _sv_map(kw: str) -> int:
        v = (dfs_map.get(kw.lower(), {}) or {}).get("search_volume")
        try:
            return int(v) if v is not None else 0
        except Exception:
            return 0

    with_vol = [k for k in merged if _sv_map(k) > 0]
    no_vol = [k for k in merged if _sv_map(k) <= 0]
    with_vol.sort(key=_sv_map, reverse=True)
    scored_keywords = (with_vol + no_vol)[: max(1, int(args.analysis_limit))]

    # Optional GSC
    gsc_rows: Dict[str, Dict[str, Any]] = {}
    gsc_notes: List[str] = []
    if args.with_gsc:
        site_url = (os.environ.get("GSC_SITE_URL") or "").strip()
        sa_json = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
        if not site_url:
            gsc_notes.append("Missing GSC_SITE_URL; skipping GSC.")
        elif not sa_json or not os.path.isfile(sa_json):
            gsc_notes.append("Missing/invalid GOOGLE_APPLICATION_CREDENTIALS; skipping GSC.")
        else:
            svc = _maybe_build_gsc_service(sa_json)
            if svc is None:
                gsc_notes.append("google client libraries not available; skipping GSC.")
            else:
                end = date.today() - timedelta(days=1)
                start = end - timedelta(days=max(1, int(args.gsc_days)))
                for kw in scored_keywords[: max(1, int(args.gsc_limit))]:
                    stat = gsc_exact_query_stats(svc=svc, site_url=site_url, start_date=start, end_date=end, keyword=kw)
                    if stat is None:
                        continue
                    gsc_rows[kw.lower()] = {
                        "keyword": kw,
                        "range_start": _ymd(start),
                        "range_end": _ymd(end),
                        "clicks": stat.clicks,
                        "impressions": stat.impressions,
                        "ctr": stat.ctr,
                        "avg_position": stat.avg_position,
                    }

    # Build a unified table
    rows_out: List[Dict[str, Any]] = []
    for kw in scored_keywords:
        m = dfs_map.get(kw.lower(), {})
        g = gsc_rows.get(kw.lower(), {})
        rows_out.append(
            {
                "keyword": kw,
                "dfs_search_volume": m.get("search_volume"),
                "dfs_cpc": m.get("cpc"),
                "dfs_competition": m.get("competition"),
                "dfs_competition_level": m.get("competition_level"),
                "gsc_impressions": g.get("impressions"),
                "gsc_clicks": g.get("clicks"),
                "gsc_ctr": g.get("ctr"),
                "gsc_avg_position": g.get("avg_position"),
                "fetched_at": fetched_at,
            }
        )

    # Write outputs
    _write_json(
        out_dir / "inputs.json",
        {
            "seeds": seeds,
            "expanded": bool(args.expand),
            "expand_sort_by": str(args.expand_sort_by),
            "expand_limit": int(args.expand_limit),
            "analysis_limit": int(args.analysis_limit),
            "gsc_limit": int(args.gsc_limit),
            "merged_keywords_count": len(merged),
            "scored_keywords_count": len(scored_keywords),
            "location_code": location_code,
            "language_code": language_code,
            "with_gsc": bool(args.with_gsc),
            "gsc_days": int(args.gsc_days),
        },
    )
    _write_json(out_dir / "dataforseo_raw_map.json", dfs_map)
    _write_json(out_dir / "gsc_raw_map.json", {"rows": gsc_rows, "notes": gsc_notes})

    if args.expand:
        _write_json(out_dir / "dataforseo_keywords_for_keywords_items.json", expanded_items)
        _write_csv(
            out_dir / "expanded_candidates.csv",
            ["keyword", "search_volume", "cpc", "competition", "competition_level", "competition_index"],
            expanded_candidates,
        )
    _write_csv(
        out_dir / "trap_release_keyword_analysis.csv",
        [
            "keyword",
            "dfs_search_volume",
            "dfs_cpc",
            "dfs_competition",
            "dfs_competition_level",
            "gsc_impressions",
            "gsc_clicks",
            "gsc_ctr",
            "gsc_avg_position",
            "fetched_at",
        ],
        rows_out,
    )

    # Console summary
    nonzero = [r for r in rows_out if (r.get("dfs_search_volume") or 0) not in (0, "0", None, "")]
    print("OK keyword analysis")
    print("wrote:", str(out_dir / "trap_release_keyword_analysis.csv"))
    print("seed_keywords:", len(seeds))
    if args.expand:
        print("expanded_candidates:", len(expanded_candidates))
        print("merged_keywords:", len(merged))
        print("scored_keywords:", len(scored_keywords))
    print("nonzero_volume_keywords:", len(nonzero))
    if gsc_notes:
        print("gsc_notes:", "; ".join(gsc_notes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

