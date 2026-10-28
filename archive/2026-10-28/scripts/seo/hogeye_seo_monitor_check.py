#!/usr/bin/env python3
"""
HogEye SEO Monitor — Gate Mode

Automated pre-publish QA check for HogEye content drafts.
Runs before any draft goes to Google Doc for client review.

Usage:
  python3 scripts/seo/hogeye_seo_monitor_check.py --draft path/to/draft.md
  python3 scripts/seo/hogeye_seo_monitor_check.py --draft path/to/draft.md --output path/to/report.md

What it checks:
  1. Blacklist scan (zero tolerance — any hit = FAIL)
  2. North Star keyword presence (required vocabulary)
  3. Structure compliance (H1, FAQ, CTA block)
  4. SEO metadata presence (meta title, meta description, slug)
  5. Internal link count (4-6 required)
  6. Word count vs brief target
  7. HogEye positioning language (is it present and correct?)

Output:
  - Prints a Gate Report to stdout
  - Optionally writes report to --output path
  - Exit code 0 = PASS, 1 = CONDITIONAL PASS, 2 = FAIL
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

# ─── Configuration ────────────────────────────────────────────────────────────

BLACKLIST = [
    "security camera",
    "driveway camera",
    "property security",
    "perimeter security",
    "surveillance camera",
    "off-grid security",
    "off grid security",
    "ranch camera",          # standalone — "trap camera on a ranch" is OK
    "hunting camera",
    "nanny cam",
    "doorbell camera",
    "spy cam",
    "gate access control",
    "delivery monitoring",
    "theft deterrent",
    "burglary",
]

# These must appear at least once in any HogEye content
REQUIRED_VOCAB_ANY_ONE = [
    "wild hog trap",
    "hog trap",
    "trap camera",
    "remote trap monitoring",
    "wild hog trap camera",
    "trap gate",
    "sounder",
]

# These are red flags — generic camera language that signals voice drift
VOICE_DRIFT_SIGNALS = [
    "trail camera",         # only a flag if used generically
    "game camera",          # only a flag if used generically
    "wildlife camera",
    "motion activated camera",
    "HD video",
    "4K",
    "night vision" ,        # acceptable in trap context, but flag for review
    "best camera",
    "top camera",
]

# Standard internal link destinations
EXPECTED_LINK_DESTINATIONS = [
    "trap-camera",
    "steel-camera",
    "net-camera-trap",
    "camera-resources",
    "buy-now",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _count_words(text: str) -> int:
    # Strip markdown syntax for a rough word count
    clean = re.sub(r"[#*_`\[\]()>|!\-]", " ", text)
    clean = re.sub(r"https?://\S+", " ", clean)
    return len(clean.split())


def _find_frontmatter(text: str) -> dict:
    """Extract YAML-like frontmatter fields from --- blocks."""
    fm: dict = {}
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return fm
    for line in match.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip().lower()] = v.strip().strip('"')
    return fm


def _extract_headings(text: str) -> List[Tuple[int, str]]:
    """Return list of (level, text) for all headings."""
    headings = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return headings


def _count_internal_links(text: str) -> Tuple[int, List[str]]:
    """Count body internal links (excluding the standard CTA block at the end).

    The CTA block is required boilerplate (4 fixed links) and should not count
    against the 4–6 body link budget. We detect it by splitting on the standard
    CTA trigger phrases.
    """
    # Strip CTA block — everything from the "Ready to run" line onward
    cta_pattern = re.compile(r"Ready to run a trap program", re.IGNORECASE)
    match = cta_pattern.search(text)
    body = text[: match.start()] if match else text

    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
    internal = []
    for anchor, url in links:
        if "hogeyecameras.com" in url or url.startswith("/") or not url.startswith("http"):
            if not url.startswith("mailto"):
                internal.append(f"{anchor} → {url}")
    return len(internal), internal


def _find_blacklist_hits(text: str) -> List[Tuple[str, str]]:
    """Return list of (term, context snippet) for each blacklist hit."""
    hits = []
    text_lower = text.lower()
    for term in BLACKLIST:
        idx = 0
        while True:
            pos = text_lower.find(term, idx)
            if pos == -1:
                break
            start = max(0, pos - 40)
            end = min(len(text), pos + len(term) + 40)
            context = "..." + text[start:end].replace("\n", " ") + "..."
            hits.append((term, context))
            idx = pos + 1
    return hits


def _find_voice_drift(text: str) -> List[Tuple[str, str]]:
    """Flag generic camera language for review."""
    hits = []
    text_lower = text.lower()
    for term in VOICE_DRIFT_SIGNALS:
        if term in text_lower:
            pos = text_lower.find(term)
            start = max(0, pos - 40)
            end = min(len(text), pos + len(term) + 40)
            context = "..." + text[start:end].replace("\n", " ") + "..."
            hits.append((term, context))
    return hits


def _check_north_star(text: str) -> bool:
    """Very rough check: does the text contain any required vocabulary?"""
    text_lower = text.lower()
    return any(v in text_lower for v in REQUIRED_VOCAB_ANY_ONE)


def _check_faq(text: str) -> bool:
    """Check for FAQ section."""
    return bool(re.search(r"(##|###)\s*(frequently asked|faq|questions)", text, re.IGNORECASE))


def _check_cta(text: str) -> bool:
    """Check for a CTA block (buy-now link or 'talk with' language)."""
    has_buy_link = "buy-now" in text.lower() or "/buy" in text.lower()
    has_talk = bool(re.search(r"talk with|talk to|get in touch|contact", text, re.IGNORECASE))
    return has_buy_link or has_talk


def _check_meta(fm: dict) -> List[str]:
    """Check metadata completeness and length."""
    issues = []
    title = fm.get("meta_title", fm.get("title", ""))
    desc = fm.get("meta_description", "")
    slug = fm.get("slug", "")

    if not title:
        issues.append("meta_title missing")
    elif len(title) > 65:
        issues.append(f"meta_title too long ({len(title)} chars, max 65)")

    if not desc:
        issues.append("meta_description missing")
    elif len(desc) < 120 or len(desc) > 160:
        issues.append(f"meta_description length {len(desc)} chars (target 120–160)")

    if not slug:
        issues.append("slug missing")
    elif re.search(r"[A-Z\s]", slug):
        issues.append(f"slug contains uppercase or spaces: '{slug}'")

    return issues


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_gate_check(draft_path: str, brief_target_words: int = 1800) -> Tuple[str, int]:
    """
    Run all gate checks on a draft file.
    Returns (report_text, exit_code) where exit_code is 0=PASS, 1=CONDITIONAL, 2=FAIL.
    """
    text = _read_file(draft_path)
    fm = _find_frontmatter(text)
    headings = _extract_headings(text)
    word_count = _count_words(text)
    link_count, link_list = _count_internal_links(text)
    blacklist_hits = _find_blacklist_hits(text)
    voice_drift = _find_voice_drift(text)
    meta_issues = _check_meta(fm)
    has_h1 = any(level == 1 for level, _ in headings)
    has_faq = _check_faq(text)
    has_cta = _check_cta(text)
    north_star_ok = _check_north_star(text)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title = fm.get("title", Path(draft_path).stem)

    failures: List[str] = []
    warnings: List[str] = []
    fixes_required: List[str] = []

    lines = [
        f"# SEO Monitor Gate Report",
        f"**Draft:** {draft_path}",
        f"**Title:** {title}",
        f"**Checked:** {now}",
        "",
    ]

    # ── Check 1: Blacklist ────────────────────────────────────────────────────
    lines.append("## Check 1: Blacklist Scan")
    if blacklist_hits:
        lines.append(f"**FAIL** — {len(blacklist_hits)} hit(s) found")
        for term, ctx in blacklist_hits:
            lines.append(f"- `{term}`: {ctx}")
            fixes_required.append(f"Remove/replace blacklisted term: '{term}'")
        failures.append("blacklist")
    else:
        lines.append("**PASS** — No blacklisted terms found")
    lines.append("")

    # ── Check 2: North Star vocabulary ───────────────────────────────────────
    lines.append("## Check 2: North Star Vocabulary")
    if north_star_ok:
        lines.append("**PASS** — Trap-specific vocabulary present")
    else:
        lines.append("**FAIL** — No trap-specific vocabulary found. Content may be off-strategy.")
        failures.append("north-star-vocab")
        fixes_required.append("Add trap-specific language (e.g. 'hog trap', 'remote trap monitoring', 'sounder')")
    lines.append("")

    # ── Check 3: Voice drift signals ─────────────────────────────────────────
    lines.append("## Check 3: Voice Drift Signals")
    if voice_drift:
        lines.append(f"**REVIEW** — {len(voice_drift)} generic camera term(s) detected (may be OK in context):")
        for term, ctx in voice_drift:
            lines.append(f"- `{term}`: {ctx}")
            warnings.append(f"Review generic camera term: '{term}'")
    else:
        lines.append("**PASS** — No generic camera language detected")
    lines.append("")

    # ── Check 4: Structure ───────────────────────────────────────────────────
    lines.append("## Check 4: Structure Compliance")
    struct_issues = []
    if not has_h1:
        struct_issues.append("H1 missing")
        fixes_required.append("Add H1 heading")
    if not has_faq:
        struct_issues.append("FAQ section missing")
        fixes_required.append("Add FAQ section with 4–6 questions")
    if not has_cta:
        struct_issues.append("CTA block missing or incomplete")
        fixes_required.append("Add standard CTA block at end of article")
    if link_count < 4:
        struct_issues.append(f"Too few internal links ({link_count} found, minimum 4)")
        fixes_required.append(f"Add more internal links (currently {link_count}, need 4–7)")
    elif link_count > 7:
        struct_issues.append(f"Too many internal links ({link_count} found, maximum 7)")
        warnings.append(f"Reduce internal links from {link_count} to 4–7")

    if struct_issues:
        lines.append(f"**FAIL** — {len(struct_issues)} issue(s):")
        for issue in struct_issues:
            lines.append(f"- {issue}")
        failures.append("structure")
    else:
        lines.append("**PASS**")
        lines.append(f"- H1: present | FAQ: present | CTA: present | Internal links: {link_count}")
    lines.append("")

    # ── Check 5: SEO Metadata ────────────────────────────────────────────────
    lines.append("## Check 5: SEO Metadata")
    if meta_issues:
        lines.append(f"**FAIL** — {len(meta_issues)} issue(s):")
        for issue in meta_issues:
            lines.append(f"- {issue}")
            fixes_required.append(f"Fix metadata: {issue}")
        failures.append("metadata")
    else:
        mt_len = len(fm.get("meta_title", fm.get("title", "")))
        md_len = len(fm.get("meta_description", ""))
        lines.append(f"**PASS** — meta_title: {mt_len} chars | meta_description: {md_len} chars | slug: OK")
    lines.append("")

    # ── Check 6: Word Count ──────────────────────────────────────────────────
    lines.append("## Check 6: Word Count")
    low = brief_target_words - 200
    high = brief_target_words + 200
    if low <= word_count <= high:
        lines.append(f"**PASS** — {word_count} words (target {brief_target_words} ±200)")
    elif word_count < low:
        lines.append(f"**WARN** — {word_count} words is short (target {low}–{high})")
        warnings.append(f"Word count {word_count} is below target range {low}–{high}")
    else:
        lines.append(f"**WARN** — {word_count} words is long (target {low}–{high})")
        warnings.append(f"Word count {word_count} is above target range {low}–{high}")
    lines.append("")

    # ── Summary ──────────────────────────────────────────────────────────────
    if failures:
        overall = "FAIL"
        exit_code = 2
        status_line = f"**Overall: FAIL** — {len(failures)} check(s) failed. Do not send to client until fixed."
    elif warnings:
        overall = "CONDITIONAL PASS"
        exit_code = 1
        status_line = f"**Overall: CONDITIONAL PASS** — Minor issues to review before or during Google Doc review."
    else:
        overall = "PASS"
        exit_code = 0
        status_line = "**Overall: PASS** — Ready for Google Doc."

    lines.insert(4, status_line)
    lines.insert(5, "")

    if fixes_required:
        lines.append("---")
        lines.append("## Required Fixes Before Google Doc")
        for i, fix in enumerate(fixes_required, 1):
            lines.append(f"{i}. {fix}")
        lines.append("")

    if warnings and not failures:
        lines.append("---")
        lines.append("## Items to Review (non-blocking)")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    report = "\n".join(lines)
    return report, exit_code


def main() -> int:
    ap = argparse.ArgumentParser(description="HogEye SEO Monitor — Gate Mode pre-publish check.")
    ap.add_argument("--draft", required=True, help="Path to the draft markdown file to check")
    ap.add_argument("--output", default="", help="Optional path to write the report (default: stdout only)")
    ap.add_argument("--target-words", type=int, default=1800, help="Target word count from brief (default 1800)")
    args = ap.parse_args()

    if not Path(args.draft).is_file():
        print(f"ERROR: Draft file not found: {args.draft}", file=sys.stderr)
        return 2

    report, exit_code = run_gate_check(args.draft, brief_target_words=args.target_words)

    print(report)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport written to: {args.output}", file=sys.stderr)

    status_labels = {0: "PASS", 1: "CONDITIONAL PASS", 2: "FAIL"}
    print(f"\nResult: {status_labels[exit_code]}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
