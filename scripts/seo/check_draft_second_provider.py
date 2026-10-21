#!/usr/bin/env python3
"""WRITING_LOOP.md phase 4: a provider that did not write the draft reads it once.

OpenAI writes HogEye drafts, so Gemini checks them (there is no xAI key on this
machine; add one and switch to Grok to match the loop exactly). The checker
names only what fails. It does not rewrite the article.

    ./.venv/bin/python scripts/seo/check_draft_second_provider.py \\
        --post content/posts/oct26_01_wp_draft.json \\
        --brief workspace/content_pipeline/monthly/2026-10/briefs/oct26_01.json

GEMINI_API_KEY comes from the environment, else from the hub repo's .dev.vars.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTS = REPO_ROOT / "workspace" / "brand_truth" / "PRODUCT_FACTS.md"
HUB_DEV_VARS = REPO_ROOT.parent / "Wildlife Dominion Client Dashboard" / ".dev.vars"
GEMINI_MODEL = os.getenv("CHECKER_MODEL", "gemini-pro-latest")

CHECKER_PROMPT = """You check one HogEye blog draft before a human reads it. A different AI wrote it.

HogEye is a cellular camera on a wild hog trap. The landowner watches the trap live in the HogEye app and, when the whole sounder is inside, sends the close command from the phone. The camera never decides or closes on its own; the reader does.

Name only what fails. Do not rewrite the article and do not suggest style changes. The failures you may name:

1. wrong_fact: a claim that contradicts the facts file or the brief's facts; a price, number, spec, or capture result in neither; the camera closing the trap automatically; the reader called a rancher; HogEye framed as security, surveillance, or property watching; any claim about a Mini AI camera; screwworm treatment or medication advice; a product called anything but "HogEye Camera" or "HogEye Mini Camera".
2. opening: the first paragraph could not be said out loud on a phone call to a landowner standing at their trap, names the page or article, or opens with a statistic or "Many landowners face the challenge".
3. repeat: the draft says a step, rule, or point it already said, or duplicates an existing page listed below instead of answering this reader's sentence.
4. rule_as_prose: a sentence that recites a rule instead of helping the reader, such as what the camera does not do, what HogEye is not, or what the article covers.
5. competitor_link: a link to a competitor's site.
6. forced_keyword: the target keyword is forced into broken English.
7. off_sentence: the draft does not teach the approved reader sentence. It does not need to quote the sentence; it fails only if a reader would not come away able to make that move.

Return JSON only: {"verdict": "pass" | "fail", "failures": [{"type": "...", "quote": "<exact words from the draft>", "why": "<one sentence>"}]}
"""


def gemini_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key and HUB_DEV_VARS.exists():
        for line in HUB_DEV_VARS.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set and was not found in the hub .dev.vars.")
    return key


def _text(markup: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup or "")).strip()


def existing_pages(brief: dict) -> list[str]:
    pages = [link["url"] for link in brief.get("internal_links", []) if link.get("url")]
    if brief.get("existing_url"):
        pages.append(brief["existing_url"])
    return pages


def check(post: dict, brief: dict, api_key: str) -> dict:
    payload = {
        "approved_reader_sentence": brief.get("reader_sentence"),
        "target_keyword": brief.get("target_keyword"),
        "brief_facts": brief.get("key_points", []),
        "existing_pages_on_site": existing_pages(brief),
        "draft": {
            "title": post.get("title"),
            "meta_description": post.get("meta_description"),
            "html": post.get("content"),
        },
        "facts_file": FACTS.read_text(encoding="utf-8"),
    }
    res = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": api_key},
        json={
            "systemInstruction": {"parts": [{"text": CHECKER_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": json.dumps(payload)}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=180,
    )
    res.raise_for_status()
    result = json.loads(res.json()["candidates"][0]["content"]["parts"][0]["text"])
    draft_text = _text(post.get("content", ""))
    # A quote the draft does not contain is the checker's invention, not a failure.
    for failure in result.get("failures", []):
        failure["quote_found"] = _text(failure.get("quote", "")) in draft_text
    result["model"] = GEMINI_MODEL
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--post", required=True, type=Path)
    parser.add_argument("--brief", required=True, type=Path)
    args = parser.parse_args()

    post = json.loads(args.post.read_text(encoding="utf-8"))
    brief = json.loads(args.brief.read_text(encoding="utf-8"))
    result = check(post, brief, gemini_key())
    post["secondProviderCheck"] = result
    args.post.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("verdict") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
