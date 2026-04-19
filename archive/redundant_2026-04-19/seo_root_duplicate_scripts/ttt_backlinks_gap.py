#!/usr/bin/env python3
"""
Backlinks gap analysis using DataForSEO Backlinks API (Live-only).

Inputs:
  - work/seo/plan/{client}_serp_competitor_domains.csv

Outputs (CSV) under work/seo/plan/ (git-ignored):
  - {client}_backlinks_referring_domains_target.csv
  - {client}_backlinks_referring_domains_competitors.csv
  - {client}_backlinks_gap_domains.csv

This produces a practical "who links to competitors but not the target site" list
to drive outreach + PR + partnerships.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


def _clean_client_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "client"


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


def _infer_domain_from_env() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    return (urlparse(wp_site).hostname or "").strip().lower()


def _dfs_post(login: str, password: str, path: str, payload: list[dict], timeout: int = 90) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.post(url, json=payload, auth=(login, password), timeout=timeout)
    r.raise_for_status()
    return r.json()


def dfs_backlinks_referring_domains_live(
    *,
    login: str,
    password: str,
    target: str,
    limit: int,
    offset: int,
) -> Tuple[int, List[dict]]:
    data = _dfs_post(
        login,
        password,
        "/backlinks/referring_domains/live",
        [
            {
                "target": target,
                "limit": limit,
                "offset": offset,
                "exclude_internal_backlinks": True,
                "include_subdomains": True,
                "include_indirect_links": True,
                "order_by": ["rank,desc"],
            }
        ],
        timeout=120,
    )
    tasks = data.get("tasks") or []
    if not tasks:
        return 0, []
    result = (tasks[0].get("result") or [])
    if not result:
        return 0, []
    total = int(result[0].get("total_count") or 0)
    items = result[0].get("items") or []
    return total, items


def _clean_domain(d: str) -> str:
    d = (d or "").strip().lower()
    if d.startswith("www."):
        d = d[4:]
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description="Backlinks gap analysis vs SERP competitors.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--client-key", default="client", help="Prefix for default input/output file paths")
    ap.add_argument("--competitors-csv", default="", help="CSV from ttt_serp_competitors_snapshot.py (overrides --client-key default)")
    ap.add_argument("--target-domain", default="", help="Target domain (defaults to WP_SITE_URL host)")
    ap.add_argument("--max-competitors", type=int, default=8, help="How many competitor domains to include (default 8)")
    ap.add_argument("--per-domain-limit", type=int, default=200, help="Referring domains per target (default 200)")
    ap.add_argument("--offset", type=int, default=0, help="Offset for referring domains (default 0)")
    ap.add_argument("--output-dir", default="work/seo/plan", help="Output directory (default work/seo/plan)")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD (set in .env).")

    client_key = _clean_client_key(args.client_key)
    if not args.competitors_csv:
        args.competitors_csv = os.path.join(args.output_dir, f"{client_key}_serp_competitor_domains.csv")

    target_domain = _clean_domain(args.target_domain or _infer_domain_from_env())
    if not target_domain:
        raise SystemExit("Missing --target-domain and could not infer from WP_SITE_URL.")

    noise = {
        "youtube.com",
        "www.youtube.com",
        "reddit.com",
        "www.reddit.com",
        "amazon.com",
        "www.amazon.com",
        "facebook.com",
        "www.facebook.com",
    }
    comp_rows = _read_csv(args.competitors_csv)
    candidates: List[str] = []
    for r in comp_rows:
        dom = _clean_domain(r.get("domain", ""))
        if not dom or dom in noise:
            continue
        if dom == target_domain or dom.endswith("." + target_domain):
            continue
        candidates.append(dom)

    seen = set()
    competitors: List[str] = []
    for d in candidates:
        if d in seen:
            continue
        seen.add(d)
        competitors.append(d)
        if len(competitors) >= max(1, int(args.max_competitors)):
            break

    if not competitors:
        raise SystemExit("No competitor domains found from the competitor CSV.")

    fetched_at = datetime.now(timezone.utc).isoformat()

    # Fetch target referring domains
    target_total, target_items = dfs_backlinks_referring_domains_live(
        login=login,
        password=password,
        target=target_domain,
        limit=max(1, int(args.per_domain_limit)),
        offset=max(0, int(args.offset)),
    )
    target_ref_domains: Set[str] = set(_clean_domain(it.get("domain", "")) for it in target_items if it.get("domain"))

    out_target = os.path.join(args.output_dir, f"{client_key}_backlinks_referring_domains_target.csv")
    _write_csv(
        out_target,
        ["target_domain", "ref_domain", "rank", "backlinks", "first_seen", "backlinks_spam_score", "fetched_at"],
        [
            {
                "target_domain": target_domain,
                "ref_domain": _clean_domain(it.get("domain", "")),
                "rank": it.get("rank"),
                "backlinks": it.get("backlinks"),
                "first_seen": it.get("first_seen"),
                "backlinks_spam_score": it.get("backlinks_spam_score"),
                "fetched_at": fetched_at,
            }
            for it in target_items
            if it.get("domain")
        ],
    )

    # Fetch competitors referring domains and compute gap
    comp_ref_map: Dict[str, Set[str]] = {}
    comp_item_map: Dict[Tuple[str, str], dict] = {}
    out_comp_rows: List[Dict[str, object]] = []

    for comp in competitors:
        _, items = dfs_backlinks_referring_domains_live(
            login=login,
            password=password,
            target=comp,
            limit=max(1, int(args.per_domain_limit)),
            offset=max(0, int(args.offset)),
        )
        domains = set()
        for it in items:
            rd = _clean_domain(it.get("domain", ""))
            if not rd:
                continue
            domains.add(rd)
            comp_item_map[(comp, rd)] = it
            out_comp_rows.append(
                {
                    "competitor_domain": comp,
                    "ref_domain": rd,
                    "rank": it.get("rank"),
                    "backlinks": it.get("backlinks"),
                    "first_seen": it.get("first_seen"),
                    "backlinks_spam_score": it.get("backlinks_spam_score"),
                    "fetched_at": fetched_at,
                }
            )
        comp_ref_map[comp] = domains

    out_comp = os.path.join(args.output_dir, f"{client_key}_backlinks_referring_domains_competitors.csv")
    _write_csv(
        out_comp,
        ["competitor_domain", "ref_domain", "rank", "backlinks", "first_seen", "backlinks_spam_score", "fetched_at"],
        out_comp_rows,
    )

    gap_counts: Dict[str, int] = defaultdict(int)
    gap_comp_list: Dict[str, List[str]] = defaultdict(list)
    gap_best_backlinks: Dict[str, int] = defaultdict(int)

    for comp, doms in comp_ref_map.items():
        for rd in doms:
            if rd in target_ref_domains:
                continue
            gap_counts[rd] += 1
            gap_comp_list[rd].append(comp)
            it = comp_item_map.get((comp, rd)) or {}
            try:
                bl = int(it.get("backlinks") or 0)
            except Exception:
                bl = 0
            if bl > gap_best_backlinks[rd]:
                gap_best_backlinks[rd] = bl

    gap_rows: List[Dict[str, object]] = []
    for rd, cnt in sorted(gap_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        comps = gap_comp_list.get(rd, [])
        gap_rows.append(
            {
                "ref_domain": rd,
                "competitor_count": cnt,
                "competitors": ", ".join(sorted(set(comps))),
                "best_backlinks_from_a_competitor": gap_best_backlinks.get(rd, 0),
                "target_domain": target_domain,
                "target_ref_domains_in_sample": len(target_ref_domains),
                "competitors_in_sample": len(competitors),
                "per_domain_limit": int(args.per_domain_limit),
                "offset": int(args.offset),
                "target_total_ref_domains": target_total,
                "fetched_at": fetched_at,
            }
        )

    out_gap = os.path.join(args.output_dir, f"{client_key}_backlinks_gap_domains.csv")
    _write_csv(
        out_gap,
        [
            "ref_domain",
            "competitor_count",
            "competitors",
            "best_backlinks_from_a_competitor",
            "target_domain",
            "target_ref_domains_in_sample",
            "competitors_in_sample",
            "per_domain_limit",
            "offset",
            "target_total_ref_domains",
            "fetched_at",
        ],
        gap_rows,
    )

    print("OK")
    print("target_domain:", target_domain)
    print("competitors:", ", ".join(competitors))
    print("target_ref_domains_in_sample:", len(target_ref_domains), "target_total_ref_domains:", target_total)
    print("gap_domains:", len(gap_rows))
    print("wrote:", out_target)
    print("wrote:", out_comp)
    print("wrote:", out_gap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

