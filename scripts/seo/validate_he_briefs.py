#!/usr/bin/env python3
"""Validate HogEye JSON briefs before anything is drafted (WRITING_LOOP.md phases 0 and 1).

From period 2026-10 on, a brief must carry the approved reader sentence and the
search evidence that justifies the piece. Filling a paid slot is not a reason.

    ./.venv/bin/python scripts/seo/validate_he_briefs.py workspace/content_pipeline/monthly/2026-10/briefs
    ./.venv/bin/python scripts/seo/validate_he_briefs.py <brief.json> --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

SENTENCE_RULE_FROM_PERIOD = "2026-10"
EVIDENCE_SOURCES = {"gsc", "ga4", "dataforseo", "semrush", "client"}
SLOT_FILLER = re.compile(r"\bpaid count\b|\bfills? (?:the |a |an )?(?:open |empty |paid )?(?:slot|count)\b", re.I)

REQUIRED_STRINGS = ("brief_id", "external_id", "period", "type", "title", "slug", "target_keyword")
VALID_TYPES = {"new", "update"}

# A key point the writer sees must be a fact a reader could use. Rules for the
# writer ("Do not claim...", "Never say...") get written into the article.
RULE_AS_FACT = re.compile(
    r"^\s*(?:do\s+not|don't|never|avoid|must|always|only\s+(?:say|use|mention)|no\s+\w+\s+(?:claims?|framing|language))\b"
    r"|\b(?:the\s+(?:article|post|piece|writer|draft)|cite|section\s+\d)\b",
    re.I,
)


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_brief(data: Dict[str, Any]) -> List[str]:
    """Return a list of errors. Empty means the brief may be drafted."""
    if not isinstance(data, dict):
        return ["brief must be a JSON object"]
    errors: List[str] = []

    for field in REQUIRED_STRINGS:
        if not _non_empty(data.get(field)):
            errors.append(f"{field}: must be a non-empty string")
    if data.get("type") not in VALID_TYPES:
        errors.append("type: must be new or update")
    if data.get("type") == "update" and not _non_empty(data.get("existing_url")):
        errors.append("existing_url: a refresh names the live page it replaces")
    period = data.get("period")
    if _non_empty(period) and not re.fullmatch(r"\d{4}-\d{2}", period):
        errors.append("period: must be YYYY-MM")

    ceiling, floor = data.get("word_count"), data.get("min_words")
    if not (isinstance(ceiling, int) and ceiling > 0):
        errors.append("word_count: the length ceiling, a positive integer")
    if floor is not None and not (isinstance(floor, int) and isinstance(ceiling, int) and 0 < floor < ceiling):
        errors.append("min_words: optional floor, a positive integer below word_count")

    key_points = data.get("key_points")
    if not isinstance(key_points, list) or not key_points:
        errors.append("key_points: list the facts the reader can use")
    else:
        for i, point in enumerate(key_points):
            if not _non_empty(point):
                errors.append(f"key_points[{i}]: must be a non-empty string")
            elif RULE_AS_FACT.search(point):
                errors.append(f"key_points[{i}]: reads as a rule for the writer, not a fact for the reader: {point[:80]!r}")

    for i, link in enumerate(data.get("internal_links") or []):
        if not (isinstance(link, dict) and _non_empty(link.get("anchor")) and _non_empty(link.get("url"))):
            errors.append(f"internal_links[{i}]: needs anchor and url")

    if not (isinstance(data.get("categories"), list) and data["categories"]):
        errors.append("categories: at least one live WordPress category")

    pending = data.get("facts_pending")
    if pending:
        errors.append(f"facts_pending: confirm these before drafting, then empty the list: {pending}")

    if _non_empty(period) and period >= SENTENCE_RULE_FROM_PERIOD:
        errors.extend(_sentence_errors(data))
    return errors


def _sentence_errors(data: Dict[str, Any]) -> List[str]:
    """Phase 0: no draft without an approved reader sentence and a reason someone is searching."""
    errors: List[str] = []
    if not _non_empty(data.get("reader_sentence")):
        errors.append("reader_sentence: one sentence a landowner could say on the phone, the situation and the move")
    approved = data.get("sentence_approved")
    if not (isinstance(approved, dict) and _non_empty(approved.get("by")) and _non_empty(approved.get("on"))):
        errors.append('sentence_approved: needs {"by": ..., "on": "YYYY-MM-DD"}; do not draft until Jason approves')
    evidence = data.get("evidence")
    usable = [
        item for item in (evidence if isinstance(evidence, list) else [])
        if isinstance(item, dict)
        and str(item.get("source", "")).lower() in EVIDENCE_SOURCES
        and _non_empty(item.get("signal"))
    ]
    if not usable:
        errors.append(f"evidence: at least one {{source, signal}} from {sorted(EVIDENCE_SOURCES)}")
    for field in ("why_this_month", "classification", "notes"):
        value = data.get(field)
        text = value if isinstance(value, str) else json.dumps(value)
        if value and SLOT_FILLER.search(text):
            errors.append(f"{field}: filling a paid slot is not a reason to write; name the search signal or wait")
    return errors


def _collect(paths: List[Path]) -> List[Path]:
    out: List[Path] = []
    for path in paths:
        if path.is_dir():
            out.extend(sorted(p for p in path.glob("*.json") if not p.name.startswith("_")))
        else:
            out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    reports = []
    for path in _collect(args.paths):
        try:
            errors = validate_brief(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            errors = [f"invalid JSON: {exc}"]
        reports.append({"path": str(path), "ok": not errors, "errors": errors})
    ok = bool(reports) and all(r["ok"] for r in reports)
    if args.as_json:
        print(json.dumps({"ok": ok, "reports": reports}))
    else:
        if not reports:
            print("No briefs found.")
        for report in reports:
            print(f"{'PASS' if report['ok'] else 'FAIL'} {report['path']}")
            for error in report["errors"]:
                print(f"  - {error}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
