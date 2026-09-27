#!/usr/bin/env python3
"""Shared fail-closed quality checks for HogEye publish JSON."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


_TAG_RE = re.compile(r"<[^>]+>")
_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
_TLDR_RE = re.compile(
    r"^\s*<p[^>]*>\s*<strong[^>]*>\s*TL;DR:\s*</strong>(.*?)</p>",
    flags=re.I | re.S,
)
_TLDR_MIN_WORDS = 35
_TLDR_MAX_WORDS = 60

# These patterns target production scaffolding, not normal reader-facing
# instructions such as "write a one-page SOP".
_INTERNAL_PATTERNS = (
    (r"\bslug(?:\s+url)?\b", "slug label"),
    (r"\burl\b", "URL label"),
    (r"\bmeta[-\s]+(?:title|description)\b", "metadata label"),
    (r"\bfocus\s+keyword\b", "focus-keyword label"),
    (r"\btarget\s+keyword\b", "target-keyword label"),
    (r"\bword\s+(?:count|target|limit)\b", "word-count label"),
    (
        r"\b(?:draft(?:ing)?|editor(?:ial)?|internal|production|review(?:er)?|writer)"
        r"\s+(?:note|notes|commentary|feedback|instruction|instructions|label|labels)\b",
        "internal drafting or review label",
    ),
    (r"\bcommentary\s*:", "commentary label"),
    (r"\b(?:refresh|remediation)\s+(?:note|notes|pass|status|work)\b", "refresh/remediation label"),
    (
        r"\b(?:content|copy|draft|article|post|page|version)"
        r"\s+(?:refresh|remediation)\b",
        "refresh/remediation label",
    ),
    (
        r"\b(?:title|headline)\s+(?:year|date)\b|\b(?:year|date)\s+"
        r"(?:in|for)\s+(?:the\s+)?(?:title|headline)\b",
        "title-year label",
    ),
    (
        r"\b(?:article|post|page)\s+(?:job|purpose)\b|\b(?:job|purpose)\s+of\s+"
        r"(?:the\s+)?(?:article|post|page)\b",
        "article/page job label",
    ),
    (r"\b(?:claims\s+audit|research\s+pack|approved\s+brief)\b", "production label"),
    (r"\b(?:placeholder|lorem\s+ipsum|todo|tbd)\b", "placeholder"),
    (r"\[\s*needs\s+source\s*\]", "source placeholder"),
    (
        r"\[\s*(?:replace|insert|add|write|fill|section|question|answer|h[1-6])\b[^\]]*\]",
        "template placeholder",
    ),
    (r"\bpass\s+or\s+fail\b", "validation placeholder"),
    (r"\b(?:article|post)\s+(?:number|no\.?|#)\s*\d+\b", "internal article label"),
    (r"\bwrite\s+(?:a|an)\s+(?:\d+[-\s])?(?:word\s+)?(?:article|post|draft|brief|meta\s+description|seo\s+title)\b", "drafting instruction"),
    (r"\b(?:system|user)\s+prompt\b", "prompt label"),
)

_BRAND_POLICY_PATTERNS = (
    (r"\branchers?\b", "banned audience term"),
    (r"\b(?:security|surveillance)\s+(?:camera|monitoring|system)\b", "security framing"),
    (r"\b(?:property|perimeter)\s+security\b", "security framing"),
    (r"\b(?:trail|game|hunting)\s+camera\b", "generic camera framing"),
    (r"\brelease(?:\s+the)?\s+(?:net|gate)\b", "wrong trap action"),
    (r"\b(?:mini\s+ai|mini\s+starlink)\b", "unreleased product claim"),
    (r"\bunreleased\b", "unreleased product claim"),
    (
        r"\b(?:treat|medicate|apply|spray|administer)\b[^.!?]{0,50}\bscrewworm\b"
        r"|\bscrewworm\b[^.!?]{0,50}\b(?:treat|medicate|apply|spray|administer)\b",
        "screwworm treatment advice",
    ),
)


def visible_text(value: Any) -> str:
    """Return reader-facing text from HTML or a nested content value."""
    if isinstance(value, dict):
        value = (
            value.get("html")
            or value.get("md")
            or value.get("markdown")
            or value.get("raw")
            or value.get("rendered")
            or ""
        )
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.I | re.S)
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", text)).strip()


def count_words(value: Any) -> int:
    return len(_WORD_RE.findall(visible_text(value)))


def _target_words(item: Dict[str, Any]) -> Optional[int]:
    nested = item.get("brief") or item.get("post") or item.get("data") or {}
    for source in (item, nested):
        for key in (
            "targetWordCount",
            "target_word_count",
            "wordTarget",
            "word_target",
            "word_count",
        ):
            value = source.get(key) if isinstance(source, dict) else None
            if isinstance(value, bool):
                continue
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                return parsed
    return None


def _scan_fields(item: Dict[str, Any]) -> Iterable[tuple[str, Any]]:
    for key in ("title", "meta_title", "meta_description", "excerpt", "content"):
        if key in item:
            yield key, item[key]
    for key in ("question", "answer"):
        for index, faq in enumerate(item.get("faq_items") or []):
            if isinstance(faq, dict) and key in faq:
                yield f"faq_items[{index}].{key}", faq[key]


def _content_tail_findings(value: Any) -> List[Dict[str, str]]:
    """Catch explicit truncation markers or a section with no reader-facing body."""
    if isinstance(value, dict):
        value = (
            value.get("html")
            or value.get("md")
            or value.get("markdown")
            or value.get("raw")
            or value.get("rendered")
            or ""
        )
    raw = str(value or "").strip()
    text = visible_text(value)
    findings: List[Dict[str, str]] = []
    if re.search(
        r"(?:\[\s*(?:truncated|cut\s+here|continue|more)\s*\]"
        r"|\.{3}|…|\bto\s+be\s+continued\b)\s*$",
        text,
        flags=re.I,
    ):
        match = re.search(
            r"(?:\[\s*(?:truncated|cut\s+here|continue|more)\s*\]"
            r"|\.{3}|…|\bto\s+be\s+continued\b)\s*$",
            text,
            flags=re.I,
        )
        findings.append(
            {
                "field": "content",
                "label": "truncated final content",
                "match": match.group(0) if match else text[-20:],
            }
        )
    if re.search(r"<h[1-6]\b[^>]*>.*?</h[1-6]>\s*$", raw, flags=re.I | re.S):
        findings.append(
            {
                "field": "content",
                "label": "final heading has no body",
                "match": re.findall(r"<h[1-6]\b[^>]*>.*?</h[1-6]>", raw, flags=re.I | re.S)[-1],
            }
        )
    if re.search(r"(?:^|\n)\s*#{1,6}\s+\S.*\s*$", raw):
        findings.append(
            {
                "field": "content",
                "label": "final heading has no body",
                "match": raw.splitlines()[-1].strip(),
            }
        )
    return findings


def _tldr_findings(value: Any) -> List[Dict[str, str]]:
    raw = str(value or "")
    match = _TLDR_RE.search(raw)
    if not match:
        return [
            {
                "field": "content",
                "label": "missing first-block TL;DR",
                "match": "",
            }
        ]
    count = count_words(match.group(1))
    if not _TLDR_MIN_WORDS <= count <= _TLDR_MAX_WORDS:
        return [
            {
                "field": "content",
                "label": f"TL;DR must be {_TLDR_MIN_WORDS}-{_TLDR_MAX_WORDS} words",
                "match": f"{count} words",
            }
        ]
    return []


def validate_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Validate one native post object and return a machine-readable report."""
    errors: List[str] = []
    if not isinstance(item, dict):
        return {"ok": False, "errors": ["post must be a JSON object"]}

    required = {
        "title": item.get("title"),
        "meta_title": item.get("meta_title"),
        "meta_description": item.get("meta_description"),
        "focus_keyword": item.get("focus_keyword"),
        "content": visible_text(item.get("content")),
    }
    for field, value in required.items():
        if not str(value or "").strip():
            errors.append(f"missing reader-facing {field}")

    findings: List[Dict[str, str]] = []
    for field, value in _scan_fields(item):
        text = visible_text(value)
        for pattern, label in _INTERNAL_PATTERNS:
            match = re.search(pattern, text, flags=re.I)
            if match:
                findings.append(
                    {
                        "field": field,
                        "label": label,
                        "match": match.group(0),
                    }
                )
        for pattern, label in _BRAND_POLICY_PATTERNS:
            match = re.search(pattern, text, flags=re.I)
            if match:
                findings.append(
                    {
                        "field": field,
                        "label": label,
                        "match": match.group(0),
                    }
                )
    if "content" in item:
        findings.extend(_tldr_findings(item["content"]))
        findings.extend(_content_tail_findings(item["content"]))
    if findings:
        errors.append("output-hygiene findings present")

    body_words = count_words(item.get("content"))
    target_words = _target_words(item)
    if target_words is None:
        errors.append("missing approved brief word target")
    else:
        if str(item.get("externalId", "")).endswith("-v2") and target_words != 800:
            errors.append("September V2 content must use the August-standard 800-word target")
        low = math.ceil(target_words * 0.95)
        high = math.floor(target_words * 1.05)
        if body_words < low or body_words > high:
            errors.append(
                f"body word count {body_words} outside ±5% target "
                f"{target_words} ({low}-{high})"
            )

    return {
        "ok": not errors,
        "errors": errors,
        "findings": findings,
        "wordCount": body_words,
        "targetWordCount": target_words,
    }


def validate_path(path: Path) -> Dict[str, Any]:
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ok": False, "errors": [f"invalid JSON: {exc}"]}
    report = validate_item(item)
    report["path"] = str(path)
    report["externalId"] = item.get("externalId") if isinstance(item, dict) else None
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HogEye publish JSON quality.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    reports = [validate_path(path) for path in args.paths]
    ok = all(report["ok"] for report in reports)
    if args.as_json:
        print(json.dumps({"ok": ok, "reports": reports}, ensure_ascii=False))
    else:
        for report in reports:
            status = "PASS" if report["ok"] else "FAIL"
            print(
                f"{status} {report.get('path', '<unknown>')} "
                f"words={report.get('wordCount', '?')} "
                f"target={report.get('targetWordCount', '?')}"
            )
            for error in report.get("errors", []):
                print(f"  - {error}")
            for finding in report.get("findings", []):
                print(
                    f"  - {finding['field']}: {finding['label']} "
                    f"({finding['match']!r})"
                )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
