#!/usr/bin/env python3
"""
Normalize a Semrush "Organic Traffic Insights" CSV export into clean, tabular CSVs.

Input format is a report-style CSV:
  - Summary stats rows
  - A "Landing pages" table
  - Repeated blocks:
      <landing page URL>
      Search Query,Clicks,Trend,Impressions,Trend,CTR %,Trend %,Position,Trend
      <query rows...>

Outputs (written to --outdir):
  - landing_pages.csv
  - queries_by_page.csv
  - opportunities.csv (basic "striking distance" filter + score)
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


def _strip_bom(s: str) -> str:
    return s.lstrip("\ufeff")


def _is_blank(line: str) -> bool:
    return not line.strip()


def _looks_like_url(line: str) -> bool:
    s = line.strip()
    return s.startswith("http://") or s.startswith("https://")


def _parse_csv_line(line: str) -> List[str]:
    # Robust parsing for quoted commas etc.
    return next(csv.reader([line], skipinitialspace=False))


def _to_int(val: str) -> Optional[int]:
    s = val.strip().replace(",", "")
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _to_float(val: str) -> Optional[float]:
    s = val.strip().replace("%", "").replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _url_key(url: str) -> str:
    """
    A stable key for joining: host + normalized path, ignoring query/fragment and scheme.
    - Lowercases host
    - Removes trailing slash (except root)
    """
    u = url.strip()
    try:
        p = urlparse(u)
    except Exception:
        return u

    host = (p.netloc or "").lower()
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return f"{host}{path}"


def _canonical_url(url: str) -> str:
    """
    Canonicalized URL string for readability (https, no query/fragment, normalized path).
    """
    u = url.strip()
    try:
        p = urlparse(u)
    except Exception:
        return u
    host = (p.netloc or "").lower()
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return f"https://{host}{path}"


@dataclass
class LandingPageRow:
    url_raw: str
    url_canonical: str
    url_key: str
    search_queries: Optional[int]
    search_queries_trend: Optional[float]
    users: Optional[int]
    new_users: Optional[int]
    sessions: Optional[int]
    engaged_sessions: Optional[int]
    engagement_rate: Optional[float]
    conversions: Optional[float]
    avg_engagement_time: str


@dataclass
class QueryRow:
    url_raw: str
    url_canonical: str
    url_key: str
    query: str
    clicks: Optional[int]
    clicks_trend: Optional[float]
    impressions: Optional[int]
    impressions_trend: Optional[float]
    ctr_pct: Optional[float]
    ctr_trend: Optional[float]
    position: Optional[float]
    position_trend: Optional[float]


def parse_landing_pages(lines: List[str]) -> Tuple[List[str], List[LandingPageRow], int]:
    """
    Returns: (header_fields, rows, next_index_after_section)
    """
    i = 0
    header: List[str] = []
    rows: List[LandingPageRow] = []

    while i < len(lines):
        if _is_blank(lines[i]):
            i += 1
            continue
        cells = _parse_csv_line(_strip_bom(lines[i]))
        if cells and cells[0].strip() == "Landing pages":
            header = [c.strip() for c in cells]
            i += 1
            break
        i += 1

    # Parse until first blank line after table (or until a non-url line)
    while i < len(lines):
        if _is_blank(lines[i]):
            # end of table
            break
        if not _looks_like_url(lines[i]):
            break
        cells = _parse_csv_line(lines[i])
        # Expected columns:
        # Landing pages,Search queries,Search queries Trend,Users,New Users,Sessions,Engaged Sessions,Engagement rate,Conversions,Av. engagement time
        url = cells[0].strip()
        lp = LandingPageRow(
            url_raw=url,
            url_canonical=_canonical_url(url),
            url_key=_url_key(url),
            search_queries=_to_int(cells[1]) if len(cells) > 1 else None,
            search_queries_trend=_to_float(cells[2]) if len(cells) > 2 else None,
            users=_to_int(cells[3]) if len(cells) > 3 else None,
            new_users=_to_int(cells[4]) if len(cells) > 4 else None,
            sessions=_to_int(cells[5]) if len(cells) > 5 else None,
            engaged_sessions=_to_int(cells[6]) if len(cells) > 6 else None,
            engagement_rate=_to_float(cells[7]) if len(cells) > 7 else None,
            conversions=_to_float(cells[8]) if len(cells) > 8 else None,
            avg_engagement_time=(cells[9].strip() if len(cells) > 9 else ""),
        )
        rows.append(lp)
        i += 1

    # Move to first non-blank after table
    while i < len(lines) and _is_blank(lines[i]):
        i += 1

    return header, rows, i


def parse_query_blocks(lines: List[str], start_index: int) -> List[QueryRow]:
    i = start_index
    out: List[QueryRow] = []

    # Helper: find next nonblank line index
    def next_nonblank(idx: int) -> int:
        j = idx
        while j < len(lines) and _is_blank(lines[j]):
            j += 1
        return j

    while i < len(lines):
        i = next_nonblank(i)
        if i >= len(lines):
            break

        if not _looks_like_url(lines[i]):
            i += 1
            continue

        url = lines[i].strip()
        j = next_nonblank(i + 1)
        if j >= len(lines):
            break

        # Expect a "Search Query,Clicks,Trend,..." header next
        header_cells = _parse_csv_line(_strip_bom(lines[j]))
        if not header_cells or header_cells[0].strip() != "Search Query":
            # Not a query block (could be stray URL)
            i = j + 1
            continue

        i = j + 1
        url_raw = url
        url_can = _canonical_url(url_raw)
        key = _url_key(url_raw)

        # Parse query rows until blank line
        while i < len(lines):
            if _is_blank(lines[i]):
                break
            # If we hit a new URL that starts another block, stop this block.
            if _looks_like_url(lines[i]):
                # might be next block
                break
            cells = _parse_csv_line(lines[i])
            if not cells:
                i += 1
                continue

            q = cells[0].strip()
            row = QueryRow(
                url_raw=url_raw,
                url_canonical=url_can,
                url_key=key,
                query=q,
                clicks=_to_int(cells[1]) if len(cells) > 1 else None,
                clicks_trend=_to_float(cells[2]) if len(cells) > 2 else None,
                impressions=_to_int(cells[3]) if len(cells) > 3 else None,
                impressions_trend=_to_float(cells[4]) if len(cells) > 4 else None,
                ctr_pct=_to_float(cells[5]) if len(cells) > 5 else None,
                ctr_trend=_to_float(cells[6]) if len(cells) > 6 else None,
                position=_to_float(cells[7]) if len(cells) > 7 else None,
                position_trend=_to_float(cells[8]) if len(cells) > 8 else None,
            )
            out.append(row)
            i += 1

        # advance beyond blank lines
        i = next_nonblank(i + 1)

    return out


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize Semrush OTI report CSV into clean tables.")
    ap.add_argument("--input", required=True, help="Path to Semrush Organic Traffic Insights CSV export")
    ap.add_argument("--outdir", required=True, help="Output directory for normalized CSVs")
    ap.add_argument("--min-impressions", type=int, default=50, help="Min impressions for opportunities.csv")
    ap.add_argument("--min-position", type=float, default=3.0, help="Min avg position for opportunities.csv")
    ap.add_argument("--max-position", type=float, default=20.0, help="Max avg position for opportunities.csv")
    ap.add_argument("--top", type=int, default=200, help="Max rows in opportunities.csv")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    _, landing_pages, idx = parse_landing_pages(lines)
    queries = parse_query_blocks(lines, idx)

    fetched_at = datetime.now(timezone.utc).isoformat()

    landing_rows: List[Dict[str, Any]] = []
    for r in landing_pages:
        landing_rows.append(
            {
                "url_raw": r.url_raw,
                "url_canonical": r.url_canonical,
                "url_key": r.url_key,
                "search_queries": r.search_queries,
                "search_queries_trend": r.search_queries_trend,
                "users": r.users,
                "new_users": r.new_users,
                "sessions": r.sessions,
                "engaged_sessions": r.engaged_sessions,
                "engagement_rate": r.engagement_rate,
                "conversions": r.conversions,
                "avg_engagement_time": r.avg_engagement_time,
                "fetched_at": fetched_at,
            }
        )

    query_rows: List[Dict[str, Any]] = []
    for q in queries:
        query_rows.append(
            {
                "url_raw": q.url_raw,
                "url_canonical": q.url_canonical,
                "url_key": q.url_key,
                "query": q.query,
                "clicks": q.clicks,
                "clicks_trend": q.clicks_trend,
                "impressions": q.impressions,
                "impressions_trend": q.impressions_trend,
                "ctr_pct": q.ctr_pct,
                "ctr_trend": q.ctr_trend,
                "position": q.position,
                "position_trend": q.position_trend,
                "fetched_at": fetched_at,
            }
        )

    # Build "opportunities" list: basic striking distance filter + simple score.
    opp: List[Dict[str, Any]] = []
    for r in query_rows:
        imp = r.get("impressions")
        pos = r.get("position")
        ctr = r.get("ctr_pct") or 0.0
        if imp is None or pos is None:
            continue
        if imp < args.min_impressions:
            continue
        if pos < args.min_position or pos > args.max_position:
            continue
        # simple: more impressions + lower CTR => more upside
        score = float(imp) * (1.0 - (ctr / 100.0))
        opp.append({**r, "opportunity_score": round(score, 3)})

    opp.sort(key=lambda x: (x.get("opportunity_score") or 0.0), reverse=True)
    opp = opp[: max(0, args.top)]

    out_landing = os.path.join(args.outdir, "landing_pages.csv")
    out_queries = os.path.join(args.outdir, "queries_by_page.csv")
    out_opp = os.path.join(args.outdir, "opportunities.csv")

    write_csv(
        out_landing,
        [
            "url_raw",
            "url_canonical",
            "url_key",
            "search_queries",
            "search_queries_trend",
            "users",
            "new_users",
            "sessions",
            "engaged_sessions",
            "engagement_rate",
            "conversions",
            "avg_engagement_time",
            "fetched_at",
        ],
        landing_rows,
    )
    write_csv(
        out_queries,
        [
            "url_raw",
            "url_canonical",
            "url_key",
            "query",
            "clicks",
            "clicks_trend",
            "impressions",
            "impressions_trend",
            "ctr_pct",
            "ctr_trend",
            "position",
            "position_trend",
            "fetched_at",
        ],
        query_rows,
    )
    write_csv(
        out_opp,
        [
            "url_canonical",
            "url_key",
            "query",
            "impressions",
            "ctr_pct",
            "position",
            "clicks",
            "opportunity_score",
            "fetched_at",
        ],
        [
            {
                "url_canonical": r.get("url_canonical"),
                "url_key": r.get("url_key"),
                "query": r.get("query"),
                "impressions": r.get("impressions"),
                "ctr_pct": r.get("ctr_pct"),
                "position": r.get("position"),
                "clicks": r.get("clicks"),
                "opportunity_score": r.get("opportunity_score"),
                "fetched_at": r.get("fetched_at"),
            }
            for r in opp
        ],
    )

    print("Normalized Semrush OTI report")
    print(f"- Input: {args.input}")
    print(f"- Landing pages: {len(landing_rows)} rows -> {out_landing}")
    print(f"- Queries: {len(query_rows)} rows -> {out_queries}")
    print(f"- Opportunities: {len(opp)} rows -> {out_opp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

