#!/usr/bin/env python3
"""
Filter Semrush OTI normalized CSVs to non-branded queries.

Default "brand" logic is intentionally simple: exclude any query containing "lakota"
case-insensitively. This matches: "camp lakota", "lakota camp", "camp.lakota", etc.
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Dict, Iterable, List


def is_nonbrand(query: str) -> bool:
    return "lakota" not in (query or "").lower()


def read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, fieldnames: List[str], rows: Iterable[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Filter Semrush OTI opportunities to non-branded queries.")
    ap.add_argument("--input", required=True, help="Path to opportunities.csv (from normalize_semrush_oti.py)")
    ap.add_argument("--output", required=True, help="Path to write nonbrand_opportunities.csv")
    args = ap.parse_args()

    rows = read_csv(args.input)
    if not rows:
        write_csv(args.output, [], [])
        return 0

    fieldnames = list(rows[0].keys())
    filtered = [r for r in rows if is_nonbrand(r.get("query", ""))]

    # Keep existing order (already sorted by opportunity_score in our generator).
    write_csv(args.output, fieldnames, filtered)
    print(f"Non-brand rows: {len(filtered)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

