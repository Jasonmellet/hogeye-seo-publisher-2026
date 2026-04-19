#!/usr/bin/env python3
"""
Fetch sitemap(s) and output a URL inventory CSV.

Output (in --output-dir):
  - Benchmark_Sitemap_Inventory.csv

This is a fast, no-GSC-needed baseline of what URLs *should* exist and be indexable.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from dotenv import load_dotenv


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _infer_site_from_env() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    return wp_site.rstrip("/")


def _fetch_text(url: str, timeout: int = 30) -> str:
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "TTT-SEO-Benchmark/1.0"})
    r.raise_for_status()
    return r.text


def _extract_sitemaps_from_robots(robots_txt: str, base_url: str) -> List[str]:
    sitemaps = []
    for line in robots_txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("sitemap:"):
            v = line.split(":", 1)[1].strip()
            if v:
                sitemaps.append(v)
    if sitemaps:
        return sitemaps
    return [urljoin(base_url + "/", "/sitemap.xml")]


def _parse_sitemap_xml(xml_text: str) -> Tuple[List[str], List[Tuple[str, Optional[str]]]]:
    """
    Return (child_sitemaps, urls_with_lastmod)

    Lightweight parsing via regex to avoid adding dependencies.
    """

    def clean(v: str) -> str:
        v = (v or "").strip()
        # handle <![CDATA[...]]> wrappers (common in WP sitemaps)
        if v.startswith("<![CDATA[") and v.endswith("]]>"):
            v = v[len("<![CDATA[") : -len("]]>")].strip()
        return v

    child = [clean(v) for v in re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.IGNORECASE | re.DOTALL)]
    is_index = bool(re.search(r"<sitemapindex", xml_text, flags=re.IGNORECASE))
    if is_index:
        return child, []

    urls: List[Tuple[str, Optional[str]]] = []
    for block in re.findall(r"<url>(.*?)</url>", xml_text, flags=re.IGNORECASE | re.DOTALL):
        loc_m = re.search(r"<loc>(.*?)</loc>", block, flags=re.IGNORECASE | re.DOTALL)
        if not loc_m:
            continue
        loc = clean(loc_m.group(1))
        lm_m = re.search(r"<lastmod>(.*?)</lastmod>", block, flags=re.IGNORECASE | re.DOTALL)
        lastmod = clean(lm_m.group(1)) if lm_m else None
        urls.append((loc, lastmod))
    return [], urls


def _head_status(url: str) -> str:
    try:
        r = requests.head(url, timeout=20, allow_redirects=True, headers={"User-Agent": "TTT-SEO-Benchmark/1.0"})
        return str(r.status_code)
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch sitemap inventory and write Benchmark_Sitemap_Inventory.csv")
    ap.add_argument("--project-root", default=os.getcwd(), help="Project root (to load .env)")
    ap.add_argument("--site", default="", help="Base site URL (defaults to WP_SITE_URL)")
    ap.add_argument("--output-dir", required=True, help="Benchmark output directory")
    ap.add_argument("--max-urls", type=int, default=5000, help="Safety cap for total URLs")
    ap.add_argument("--check-http", action="store_true", help="Also HEAD each URL to get status code (slower)")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    site = (args.site or _infer_site_from_env()).strip().rstrip("/")
    if not site:
        raise SystemExit("Missing --site and WP_SITE_URL not set.")

    robots_url = urljoin(site + "/", "/robots.txt")
    try:
        robots_txt = _fetch_text(robots_url, timeout=30)
    except Exception:
        robots_txt = ""

    sitemap_urls = _extract_sitemaps_from_robots(robots_txt, site)

    seen_sitemaps: Set[str] = set()
    q = deque([(u, 0) for u in sitemap_urls])
    rows: List[Dict[str, object]] = []
    seen_urls: Set[str] = set()
    fetched_at = datetime.now(timezone.utc).isoformat()

    while q:
        sm_url, depth = q.popleft()
        if sm_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sm_url)
        try:
            xml = _fetch_text(sm_url, timeout=60)
        except Exception:
            continue

        child_sitemaps, urls = _parse_sitemap_xml(xml)
        for c in child_sitemaps:
            if c and c not in seen_sitemaps:
                q.append((c.strip(), depth + 1))

        for loc, lastmod in urls:
            loc = (loc or "").strip()
            if not loc:
                continue
            if loc in seen_urls:
                continue
            seen_urls.add(loc)
            if len(seen_urls) > max(1, int(args.max_urls)):
                break

            status_code = _head_status(loc) if args.check_http else ""
            rows.append(
                {
                    "url": loc,
                    "lastmod": lastmod or "",
                    "source_sitemap": sm_url,
                    "sitemap_depth": depth,
                    "http_status": status_code,
                    "fetched_at": fetched_at,
                }
            )

        if len(seen_urls) > max(1, int(args.max_urls)):
            break

    out = os.path.join(args.output_dir, "Benchmark_Sitemap_Inventory.csv")
    write_csv(out, ["url", "lastmod", "source_sitemap", "sitemap_depth", "http_status", "fetched_at"], rows)
    print(f"Wrote sitemap inventory -> {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

