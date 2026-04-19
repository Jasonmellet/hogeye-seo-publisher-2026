#!/usr/bin/env python3
"""
Create/refresh HogEye monthly phase-1 content pipeline scaffolding.

This script is file-system only. It does not call WordPress.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable, List

from repo_workspace import workspace_root


REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = workspace_root() / "content_pipeline"
TEMPLATES_ROOT = PIPELINE_ROOT / "templates"
MONTHLY_ROOT = PIPELINE_ROOT / "monthly"

QUEUE_HEADER = [
    "article_id",
    "month",
    "status",
    "target_keyword",
    "secondary_keywords",
    "search_intent",
    "content_angle",
    "approved_audience_terms",
    "internal_links",
    "cta_guidance",
    "dataforseo_source",
    "gsc_source",
    "ga4_source",
    "website_truth_sources",
    "brief_path",
    "research_pack_path",
    "draft_path",
    "qa_path",
    "handoff_path",
    "notes",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text_if_missing(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False
    path.write_text(text, encoding="utf-8")
    return True


def _ensure_queue_csv(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUEUE_HEADER)
    return True


def _normalize_article_ids(raw_ids: str) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in (raw_ids or "").split(","):
        aid = item.strip()
        if not aid:
            continue
        if aid in seen:
            continue
        seen.add(aid)
        out.append(aid)
    return out


def _iter_article_targets(month_root: Path, article_id: str) -> Iterable[tuple[Path, Path]]:
    return [
        (month_root / "briefs" / f"{article_id}_brief.md", TEMPLATES_ROOT / "brief.template.md"),
        (month_root / "research_packs" / f"{article_id}_research_pack.md", TEMPLATES_ROOT / "research_pack.template.md"),
        (month_root / "drafts" / f"{article_id}_draft.md", TEMPLATES_ROOT / "draft.template.md"),
        (month_root / "qa" / f"{article_id}_qa.md", TEMPLATES_ROOT / "qa_checklist.template.md"),
        (month_root / "handoff" / f"{article_id}_handoff.md", TEMPLATES_ROOT / "google_docs_handoff.template.md"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold monthly HogEye content pipeline files.")
    parser.add_argument("--month", required=True, help="Month key in YYYY-MM format (example: 2026-03)")
    parser.add_argument(
        "--article-ids",
        default="",
        help="Comma-separated article IDs. Creates one file set per ID from templates.",
    )
    args = parser.parse_args()

    month = args.month.strip()
    if len(month) != 7 or month[4] != "-":
        raise SystemExit("Invalid --month format. Expected YYYY-MM.")

    month_root = MONTHLY_ROOT / month
    queue_csv = month_root / "queue" / "monthly_queue.csv"
    created_items: List[str] = []

    for subdir in ["queue", "briefs", "research_packs", "drafts", "qa", "handoff"]:
        p = month_root / subdir
        p.mkdir(parents=True, exist_ok=True)
        created_items.append(f"ensured_dir:{p.relative_to(REPO_ROOT)}")

    if _ensure_queue_csv(queue_csv):
        created_items.append(f"created_file:{queue_csv.relative_to(REPO_ROOT)}")

    article_ids = _normalize_article_ids(args.article_ids)
    for article_id in article_ids:
        for out_path, template_path in _iter_article_targets(month_root, article_id):
            if not template_path.exists():
                raise SystemExit(f"Missing template: {template_path}")
            template_body = _read_text(template_path)
            header = (
                f"<!-- scaffolded_by: scripts/seo/hogeye_create_monthly_pipeline.py -->\n"
                f"<!-- month: {month} -->\n"
                f"<!-- article_id: {article_id} -->\n\n"
            )
            if _write_text_if_missing(out_path, header + template_body):
                created_items.append(f"created_file:{out_path.relative_to(REPO_ROOT)}")

    print("OK monthly pipeline scaffold")
    print(f"month: {month}")
    if article_ids:
        print(f"article_ids: {', '.join(article_ids)}")
    else:
        print("article_ids: none")
    for item in created_items:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
