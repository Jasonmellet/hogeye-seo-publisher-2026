#!/usr/bin/env python3
"""
Extract People Also Ask (PAA) questions from Google SERP for HogEye seed queries.

Uses DataForSEO SERP Live Advanced endpoint and pulls PAA items specifically.
PAA questions reveal what the audience is actually asking — ideal for content
brief generation and FAQ schema opportunities.

Input:
  - CSV with a 'keyword' column (defaults to work/seo/plan/hogeye_may_seed_keywords.csv)

Output:
  - work/seo/plan/hogeye_paa_questions.csv
    Columns: seed_keyword, question, rank_in_paa, topic_cluster (if in input), fetched_at
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


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


def _dfs_serp_live_advanced(
    *,
    login: str,
    password: str,
    keyword: str,
    location_code: int,
    language_code: str,
) -> List[dict]:
    """Pull full SERP item list (all types) for a keyword."""
    url = f"{API_BASE}/serp/google/organic/live/advanced"
    body = [
        {
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": "desktop",
            "os": "windows",
            "depth": 10,
        }
    ]
    r = requests.post(url, json=body, auth=(login, password), timeout=90)
    r.raise_for_status()
    data = r.json()
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    results = tasks[0].get("result") or []
    if not results:
        return []
    return results[0].get("items") or []


def _extract_paa_questions(items: List[dict], seed_keyword: str) -> List[Dict[str, object]]:
    """
    Walk the SERP items list and extract all PAA questions.

    DataForSEO returns PAA as items with type='people_also_ask'.
    Each has an 'items' array of elements with type='people_also_ask_element'
    and a 'title' field containing the question text.
    """
    questions: List[Dict[str, object]] = []
    for item in items:
        item_type = (item.get("type") or "").lower()
        if item_type != "people_also_ask":
            continue
        paa_elements = item.get("items") or []
        for rank, elem in enumerate(paa_elements, start=1):
            question = (elem.get("title") or "").strip()
            if not question:
                # Some responses nest the question in 'featured_title' or 'description'
                question = (elem.get("featured_title") or elem.get("description") or "").strip()
            if question:
                questions.append({
                    "seed_keyword": seed_keyword,
                    "question": question,
                    "rank_in_paa": rank,
                })
    return questions


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract PAA questions from SERP for HogEye seed queries.")
    ap.add_argument("--project-root", default=str(Path.cwd()))
    ap.add_argument(
        "--keywords-csv",
        default="work/seo/plan/hogeye_may_seed_keywords.csv",
        help="CSV with 'keyword' column (and optional 'topic_cluster')",
    )
    ap.add_argument("--keywords-col", default="keyword")
    ap.add_argument("--cluster-col", default="topic_cluster", help="Optional column for topic cluster label")
    ap.add_argument("--max-keywords", type=int, default=35, help="Max seed keywords to process (default 35)")
    ap.add_argument("--output-dir", default="work/seo/plan")
    ap.add_argument("--output", default="", help="Override output path")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in .env")

    location_code = int(os.environ.get("DATAFORSEO_LOCATION_CODE", "2840"))
    language_code = (os.environ.get("DATAFORSEO_LANGUAGE_CODE", "en") or "en").strip()

    if not os.path.isfile(args.keywords_csv):
        raise SystemExit(f"Keywords CSV not found: {args.keywords_csv}")

    input_rows = _read_csv(args.keywords_csv)
    # Build keyword -> cluster lookup
    cluster_map: Dict[str, str] = {}
    keywords: List[str] = []
    seen: set = set()
    for row in input_rows:
        kw = (row.get(args.keywords_col) or "").strip()
        if not kw or kw.lower() in seen:
            continue
        seen.add(kw.lower())
        keywords.append(kw)
        cluster_map[kw] = (row.get(args.cluster_col) or "").strip()

    keywords = keywords[: max(1, args.max_keywords)]
    fetched_at = datetime.now(timezone.utc).isoformat()

    all_rows: List[Dict[str, object]] = []
    question_dedup: set = set()

    for kw in keywords:
        print(f"Pulling SERP for: {kw!r} ...")
        items = _dfs_serp_live_advanced(
            login=login,
            password=password,
            keyword=kw,
            location_code=location_code,
            language_code=language_code,
        )
        paa = _extract_paa_questions(items, kw)
        print(f"  → {len(paa)} PAA question(s) found")

        for p in paa:
            q_key = p["question"].lower().strip()
            all_rows.append({
                "seed_keyword": p["seed_keyword"],
                "question": p["question"],
                "rank_in_paa": p["rank_in_paa"],
                "topic_cluster": cluster_map.get(kw, ""),
                "is_duplicate_question": "yes" if q_key in question_dedup else "no",
                "location_code": location_code,
                "language_code": language_code,
                "fetched_at": fetched_at,
            })
            question_dedup.add(q_key)

    out_path = args.output or os.path.join(args.output_dir, "hogeye_paa_questions.csv")
    _write_csv(
        out_path,
        ["seed_keyword", "question", "rank_in_paa", "topic_cluster",
         "is_duplicate_question", "location_code", "language_code", "fetched_at"],
        all_rows,
    )

    unique_q = len([r for r in all_rows if r["is_duplicate_question"] == "no"])
    print(f"\n{'='*60}")
    print(f"Total PAA rows: {len(all_rows)} ({unique_q} unique questions)")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
