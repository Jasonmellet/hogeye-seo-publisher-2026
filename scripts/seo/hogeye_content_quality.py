#!/usr/bin/env python3
"""Shared fail-closed quality checks for HogEye publish JSON.

These checks police what must never reach a reader: production labels, brand
policy breaks, brief rules written as prose, repeats, and prices that are not in
the product facts. They do not score keyword placement or force an exact length.
Length is a ceiling with an optional floor (WRITING_LOOP.md phase 5).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_FACTS = REPO_ROOT / "workspace" / "brand_truth" / "PRODUCT_FACTS.md"

_TAG_RE = re.compile(r"<[^>]+>")
_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)

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
    (r"\b(?:placeholder|lorem\s+ipsum|to\s+do|todo|tbd)\b", "placeholder"),
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
    # "trail camera" is a phrase readers search for, so it may appear. HogEye
    # itself is never called one.
    (r"\bhogeye(?:\s+mini)?(?:\s+camera)?\s+(?:is|as)\s+an?\s+(?:trail|game|hunting)\s+cam", "HogEye called a trail camera"),
    (r"\b(?:game|hunting)\s+camera\b", "generic camera framing"),
    (r"\brelease(?:\s+the)?\s+(?:net|gate)\b", "wrong trap action"),
    (r"\bmini\s+ai\b", "unreleased product claim"),
    # Product names are "HogEye Camera" and "HogEye Mini Camera".
    (r"\bhogeye\s+steel\b|\bsteel\s+cam(?:era)?s?\b", "retired product name (Steel)"),
    (r"\u2014", "em dash"),
    (r"\bunreleased\b", "unreleased product claim"),
    (
        r"\b(?:treat(?:ment)?|medicat(?:e|ion)|apply|spray|drug)\b.{0,50}\bscrewworm\b",
        "screwworm treatment advice",
    ),
)


# Brief rules written as prose. The October 2026 drafts said "the camera does not
# close the gate by itself" eight times across five articles. Show the reader
# sending the command instead of reciting the rule.
_RULE_LEAK_PATTERNS = (
    (
        r"\b(?:camera|cam|it|hogeye(?:\s+mini)?)\s+(?:does\s+not|doesn't|will\s+not|won't|cannot|can't|never)"
        r"\s+(?:decide|close|shut|drop|trip|trigger)\b",
        "gate rule written as prose (camera does not close/decide)",
    ),
    (r"\b(?:close|closes|shut|trigger|drop)s?\b[^.]{0,40}\b(?:by\s+itself|on\s+its\s+own)\b", "gate rule written as prose (by itself)"),
    (
        r"\bnot\s+(?:a\s+|an\s+)?(?:security|surveillance|general[-\s]property|property|perimeter)\s+"
        r"(?:camera|cam|monitor|system|tool|device)\b",
        "positioning rule written as prose (not a security camera)",
    ),
    (r"\bthis\s+(?:page|article|post|guide|hub)\b", "article talks about itself"),
    (r"\bwhat\s+this\s+(?:page|article|post|piece|guide)\s+is\s+not\b", "article lists what it is not about"),
    (
        r"\b(?:do\s+not|don't|never)\s+(?:write|import|describe|mention|narrate|cite|quote|claim|invent)\b",
        "writing rule from the brief",
    ),
    (r"\bkeywords?\b|\bsearch\s+intent\b|\bsearch\s+(?:phrase|demand)\b", "SEO planning language"),
    (r"\bnorth\s+star\b|\bbrand\s+(?:truth|baseline)\b|\bapproved\s+language\b", "internal doc name"),
    (r"\b(?:AI|ChatGPT|LLMs?)\s+(?:search|overviews?|citations?|retrieval)\b", "AI-search planning language"),
)

_PRICE_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s*(?:billion|million))?", re.I)
_REPEAT_SENTENCE_MIN_WORDS = 6
LENGTH_CEILING = 1.10
_REPEAT_NGRAM = 8
_REPEAT_NGRAM_LIMIT = 3


def _norm_price(value: str) -> str:
    return re.sub(r"[\s,]", "", value.lower()).removesuffix(".00")


def allowed_prices() -> set[str]:
    """Every dollar figure in PRODUCT_FACTS.md. A figure not in that file does not ship."""
    try:
        return {_norm_price(m) for m in _PRICE_RE.findall(PRODUCT_FACTS.read_text(encoding="utf-8"))}
    except OSError:
        return set()


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


def _repeat_findings(value: Any) -> List[Dict[str, str]]:
    """A step said twice is a repeat. Questions are skipped: an H2 can echo an FAQ."""
    text = visible_text(value)
    findings: List[Dict[str, str]] = []
    seen: Dict[str, int] = {}
    for sentence in re.split(r"(?<=[.!])\s+", text):
        norm = " ".join(re.findall(r"[a-z0-9']+", sentence.lower()))
        if len(norm.split()) < _REPEAT_SENTENCE_MIN_WORDS:
            continue
        seen[norm] = seen.get(norm, 0) + 1
        if seen[norm] == 2:
            findings.append({"field": "content", "label": "repeated sentence", "match": sentence.strip()[:160]})
    words = re.findall(r"[a-z0-9']+", text.lower())
    grams: Dict[tuple, int] = {}
    for i in range(len(words) - _REPEAT_NGRAM + 1):
        gram = tuple(words[i : i + _REPEAT_NGRAM])
        grams[gram] = grams.get(gram, 0) + 1
        if grams[gram] == _REPEAT_NGRAM_LIMIT:
            findings.append({"field": "content", "label": f"phrase repeated {_REPEAT_NGRAM_LIMIT}+ times", "match": " ".join(gram)})
    return findings


def _price_findings(fields: Iterable[tuple[str, Any]]) -> List[Dict[str, str]]:
    allowed = allowed_prices()
    findings: List[Dict[str, str]] = []
    for field, value in fields:
        for match in _PRICE_RE.findall(visible_text(value)):
            if _norm_price(match) not in allowed:
                findings.append({"field": field, "label": "price not in PRODUCT_FACTS.md", "match": match})
    return findings


def _length_bounds(item: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
    """(floor, ceiling). Ceiling is the brief's word_count; floor is optional min_words."""
    nested = item.get("brief") or item.get("post") or item.get("data") or {}
    floor = None
    for source in (item, nested):
        if not isinstance(source, dict):
            continue
        for key in ("minWords", "min_words"):
            value = source.get(key)
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                floor = value
    return floor, _target_words(item)


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
    warnings: List[str] = []
    fields = list(_scan_fields(item))
    for field, value in fields:
        text = visible_text(value)
        for pattern, label in _INTERNAL_PATTERNS + _RULE_LEAK_PATTERNS:
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
        findings.extend(_content_tail_findings(item["content"]))
        findings.extend(_repeat_findings(item["content"]))
    findings.extend(_price_findings(fields))
    if findings:
        errors.append("output-hygiene findings present")

    # Length is a ceiling, not a band. Over the ceiling by more than 10% fails;
    # under the optional floor is a warning, because a short piece that answers
    # the reader beats a padded one.
    body_words = count_words(item.get("content"))
    floor, ceiling = _length_bounds(item)
    if ceiling is None:
        errors.append("missing approved brief word ceiling (word_count)")
    elif body_words > ceiling * LENGTH_CEILING:
        errors.append(f"body word count {body_words} over the brief ceiling {ceiling}; cut what the reader does not need")
    if floor and body_words < floor:
        warnings.append(f"body word count {body_words} under the brief floor {floor}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
        "wordCount": body_words,
        "targetWordCount": ceiling,
        "minWords": floor,
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
            for warning in report.get("warnings", []):
                print(f"  - warn: {warning}")
            for finding in report.get("findings", []):
                print(
                    f"  - {finding['field']}: {finding['label']} "
                    f"({finding['match']!r})"
                )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
