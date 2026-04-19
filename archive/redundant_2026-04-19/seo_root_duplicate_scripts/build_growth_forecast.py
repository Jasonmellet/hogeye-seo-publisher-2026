#!/usr/bin/env python3
"""
Build a baseline-to-forecast scorecard for +25% organic growth planning.

Inputs:
  - Benchmark summary CSV (for baseline totals)
  - Deep GSC non-brand queries CSV (exact query baseline metrics)
  - DataForSEO rank snapshot CSV (keyword position hints)
  - Keyword list CSV (single 'keyword' column)

Outputs:
  - Forecast_25pct_assumptions.json
  - Forecast_25pct_keyword_model.csv
  - Forecast_25pct_scenarios.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


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


def to_float(v: object, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        s = str(v).strip().replace(",", "")
        return float(s) if s else default
    except Exception:
        return default


def ctr_curve(position: Optional[float]) -> float:
    """
    A pragmatic CTR-by-position curve for directional forecasting.
    """
    if position is None or position <= 0:
        return 0.003
    p = position
    if p <= 1:
        return 0.28
    if p <= 2:
        return 0.16
    if p <= 3:
        return 0.11
    if p <= 5:
        return 0.07
    if p <= 8:
        return 0.04
    if p <= 10:
        return 0.03
    if p <= 15:
        return 0.015
    if p <= 20:
        return 0.008
    return 0.003


def projected_position(current_pos: Optional[float], scenario: str) -> Optional[float]:
    if current_pos is None or current_pos <= 0:
        return None
    p = current_pos
    if scenario == "conservative":
        if p > 20:
            return 18
        if p > 10:
            return max(1.0, p - 2)
        if p > 5:
            return max(1.0, p - 1)
        return p
    if scenario == "base":
        if p > 20:
            return 12
        if p > 10:
            return max(1.0, p - 4)
        if p > 5:
            return max(1.0, p - 2)
        return max(1.0, p - 0.5)
    # best
    if p > 20:
        return 8
    if p > 10:
        return max(1.0, p - 6)
    if p > 5:
        return max(1.0, p - 3)
    return max(1.0, p - 1)


@dataclass
class ScenarioConfig:
    name: str
    capture_factor: float


def main() -> int:
    ap = argparse.ArgumentParser(description="Build +25% growth forecast scorecard artifacts.")
    ap.add_argument("--benchmark-summary", required=True, help="Path to Benchmark_Summary.csv")
    ap.add_argument("--gsc-nonbrand-queries", required=True, help="Path to GSC_Queries_NonBrand.csv")
    ap.add_argument("--dfs-rank-snapshot", required=True, help="Path to Benchmark_DataForSEO_RankSnapshot.csv")
    ap.add_argument("--keywords-csv", required=True, help="Path to keyword list CSV with `keyword` column")
    ap.add_argument("--output-dir", required=True, help="Directory to write forecast files")
    args = ap.parse_args()

    fetched_at = datetime.now(timezone.utc).isoformat()
    scenarios = [
        ScenarioConfig("conservative", 0.35),
        ScenarioConfig("base", 0.50),
        ScenarioConfig("best", 0.65),
    ]

    summary_rows = read_csv(args.benchmark_summary)
    gsc_rows = read_csv(args.gsc_nonbrand_queries)
    dfs_rows = read_csv(args.dfs_rank_snapshot)
    kw_rows = read_csv(args.keywords_csv)

    baseline_clicks_total = 0.0
    baseline_impr_total = 0.0
    for r in summary_rows:
        if (r.get("section") or "").strip() == "GSC Totals (Top Pages)":
            metric = (r.get("metric") or "").strip()
            if metric == "clicks":
                baseline_clicks_total = to_float(r.get("value"))
            elif metric == "impressions":
                baseline_impr_total = to_float(r.get("value"))

    gsc_map: Dict[str, Dict[str, float]] = {}
    for r in gsc_rows:
        q = (r.get("query") or "").strip().lower()
        if not q:
            continue
        gsc_map[q] = {
            "clicks": to_float(r.get("clicks")),
            "impressions": to_float(r.get("impressions")),
            "ctr": to_float(r.get("ctr")),
            "avg_position": to_float(r.get("avg_position")),
        }

    dfs_map: Dict[str, Dict[str, object]] = {}
    for r in dfs_rows:
        q = (r.get("keyword") or "").strip().lower()
        if not q:
            continue
        dfs_map[q] = {
            "best_position": to_float(r.get("best_position"), 0.0),
            "best_url": (r.get("best_url") or "").strip(),
        }

    keywords = []
    for r in kw_rows:
        q = (r.get("keyword") or "").strip()
        if q:
            keywords.append(q)

    model_rows: List[Dict[str, object]] = []
    scenario_incremental: Dict[str, float] = {s.name: 0.0 for s in scenarios}

    for kw in keywords:
        k = kw.lower()
        g = gsc_map.get(k, {})
        d = dfs_map.get(k, {})
        impr = float(g.get("impressions") or 0.0)
        clicks = float(g.get("clicks") or 0.0)
        gsc_pos = float(g.get("avg_position") or 0.0)
        dfs_pos = float(d.get("best_position") or 0.0)

        current_pos: Optional[float] = None
        if gsc_pos > 0:
            current_pos = gsc_pos
        elif dfs_pos > 0:
            current_pos = dfs_pos

        current_ctr_model = ctr_curve(current_pos)

        row: Dict[str, object] = {
            "keyword": kw,
            "baseline_impressions": round(impr, 2),
            "baseline_clicks": round(clicks, 2),
            "baseline_ctr_observed": round(float(g.get("ctr") or 0.0), 5),
            "current_position_estimate": round(current_pos, 2) if current_pos else "",
            "current_ctr_model": round(current_ctr_model, 5),
            "dfs_best_url": d.get("best_url") or "",
            "fetched_at": fetched_at,
        }

        for s in scenarios:
            tgt_pos = projected_position(current_pos, s.name)
            tgt_ctr = ctr_curve(tgt_pos)
            projected_clicks = impr * tgt_ctr
            incremental = max(0.0, projected_clicks - clicks)
            captured_incremental = incremental * s.capture_factor
            scenario_incremental[s.name] += captured_incremental
            row[f"{s.name}_target_position"] = round(tgt_pos, 2) if tgt_pos else ""
            row[f"{s.name}_target_ctr"] = round(tgt_ctr, 5)
            row[f"{s.name}_projected_clicks_raw"] = round(projected_clicks, 2)
            row[f"{s.name}_incremental_clicks_captured"] = round(captured_incremental, 2)

        model_rows.append(row)

    target_clicks_25 = baseline_clicks_total * 1.25
    scenario_rows: List[Dict[str, object]] = []
    for s in scenarios:
        projected_total = baseline_clicks_total + scenario_incremental[s.name]
        lift_pct = ((projected_total - baseline_clicks_total) / baseline_clicks_total * 100.0) if baseline_clicks_total > 0 else 0.0
        gap_to_25 = projected_total - target_clicks_25
        scenario_rows.append(
            {
                "scenario": s.name,
                "baseline_clicks_total": round(baseline_clicks_total, 2),
                "baseline_impressions_total": round(baseline_impr_total, 2),
                "projected_clicks_total": round(projected_total, 2),
                "projected_lift_pct": round(lift_pct, 2),
                "target_clicks_for_25pct": round(target_clicks_25, 2),
                "gap_to_25pct_target_clicks": round(gap_to_25, 2),
                "capture_factor": s.capture_factor,
                "fetched_at": fetched_at,
            }
        )

    assumptions = {
        "generated_at": fetched_at,
        "inputs": {
            "benchmark_summary": args.benchmark_summary,
            "gsc_nonbrand_queries": args.gsc_nonbrand_queries,
            "dfs_rank_snapshot": args.dfs_rank_snapshot,
            "keywords_csv": args.keywords_csv,
        },
        "scenarios": [{ "name": s.name, "capture_factor": s.capture_factor } for s in scenarios],
        "ctr_curve": {
            "1": 0.28,
            "2": 0.16,
            "3": 0.11,
            "5": 0.07,
            "8": 0.04,
            "10": 0.03,
            "15": 0.015,
            "20": 0.008,
            ">20": 0.003,
        },
        "notes": [
            "Directional model for planning, not a guarantee.",
            "GA4 integration is excluded if property access is unavailable.",
            "Projected gains are discounted by scenario capture_factor to avoid overestimation.",
        ],
    }

    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, "Forecast_25pct_keyword_model.csv")
    scenarios_path = os.path.join(out_dir, "Forecast_25pct_scenarios.csv")
    assumptions_path = os.path.join(out_dir, "Forecast_25pct_assumptions.json")

    write_csv(
        model_path,
        list(model_rows[0].keys()) if model_rows else [
            "keyword",
            "baseline_impressions",
            "baseline_clicks",
            "baseline_ctr_observed",
            "current_position_estimate",
            "current_ctr_model",
            "conservative_target_position",
            "conservative_target_ctr",
            "conservative_projected_clicks_raw",
            "conservative_incremental_clicks_captured",
            "base_target_position",
            "base_target_ctr",
            "base_projected_clicks_raw",
            "base_incremental_clicks_captured",
            "best_target_position",
            "best_target_ctr",
            "best_projected_clicks_raw",
            "best_incremental_clicks_captured",
            "dfs_best_url",
            "fetched_at",
        ],
        model_rows,
    )
    write_csv(
        scenarios_path,
        [
            "scenario",
            "baseline_clicks_total",
            "baseline_impressions_total",
            "projected_clicks_total",
            "projected_lift_pct",
            "target_clicks_for_25pct",
            "gap_to_25pct_target_clicks",
            "capture_factor",
            "fetched_at",
        ],
        scenario_rows,
    )
    with open(assumptions_path, "w", encoding="utf-8") as f:
        json.dump(assumptions, f, indent=2)

    print(f"Wrote forecast model -> {model_path} ({len(model_rows)} rows)")
    print(f"Wrote scenarios -> {scenarios_path} ({len(scenario_rows)} rows)")
    print(f"Wrote assumptions -> {assumptions_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

