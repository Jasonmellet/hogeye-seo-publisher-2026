#!/usr/bin/env python3
"""HogEye writer: one approved brief in, one article out (WRITING_LOOP.md phase 3).

The writer sees the reader sentence, the title, the keyword, the length range,
the facts, the section suggestions, and the internal links. It never sees
evidence, sources, or rules about the brief: when those went into the prompt,
the model wrote them into the article.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT_PATH = REPO_ROOT / "workspace" / "content_system" / "prompts" / "system" / "hogeye_writer_system_prompt.md"

# WRITING_LOOP.md: gpt-6 Luna, reasoning effort low, no temperature setting.
# HE_WRITER_MODEL, not OPENAI_MODEL: .env still names the old Cursor-era model.
MODEL = os.getenv("HE_WRITER_MODEL", "gpt-6-luna")
REASONING_EFFORT = os.getenv("HE_WRITER_REASONING_EFFORT", "low")
OUTPUT_KEYS = ("html_content", "meta_title", "meta_description", "excerpt", "faq")


class Writer:
    def __init__(self) -> None:
        load_dotenv(REPO_ROOT / ".env")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY is not set in .env.")
        self.client = OpenAI(api_key=api_key)
        self.model = MODEL

    def _call(self, user_prompt: str) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            reasoning_effort=REASONING_EFFORT,
            max_completion_tokens=16000,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")},
                {"role": "user", "content": user_prompt},
            ],
        )
        data = json.loads(response.choices[0].message.content or "{}")
        if not isinstance(data, dict) or not str(data.get("html_content", "")).strip():
            raise ValueError("Writer did not return html_content.")
        data["faq"] = [f for f in data.get("faq") or [] if isinstance(f, dict) and f.get("question") and f.get("answer")]
        return {key: data.get(key) for key in OUTPUT_KEYS}

    def write(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        return self._call(article_prompt(brief))

    def revise(self, brief: Dict[str, Any], draft: Dict[str, Any], problems: List[str]) -> Dict[str, Any]:
        return self._call(revision_prompt(brief, draft, problems))


def _length_line(brief: Dict[str, Any]) -> str:
    if brief.get("min_words"):
        return (
            f"LENGTH: {brief['min_words']} to {brief['word_count']} words. Get there by answering each section fully "
            "with the facts below. Never restate a step or add filler to reach it."
        )
    return f"LENGTH: at most {brief['word_count']} words. Shorter is fine when the reader has what they need."


def _facts(brief: Dict[str, Any]) -> str:
    return "\n".join(f"- {point}" for point in brief.get("key_points", [])) or "- (none)"


def article_prompt(brief: Dict[str, Any]) -> str:
    """Only the reader-facing parts of the brief. Evidence and sources stay out."""
    prompt = f"""THE SENTENCE (the article teaches this):
{brief['reader_sentence']}

TITLE: {brief['title']}
TARGET KEYWORD: {brief['target_keyword']}
{_length_line(brief)}

FACTS YOU MAY USE:
{_facts(brief)}
"""
    if brief.get("h2_outline"):
        prompt += "\nSECTIONS (suggestions; merge or drop any the reader does not need):\n"
        prompt += "".join(f"- {h2}\n" for h2 in brief["h2_outline"])
    if brief.get("internal_links"):
        prompt += "\nINTERNAL PAGES (link one only where the reader needs it next):\n"
        prompt += "".join(f"- {link['anchor']}: {link['url']}\n" for link in brief["internal_links"])
    if brief.get("faq_questions"):
        prompt += "\nFAQ QUESTIONS (answer only the ones the body did not already answer):\n"
        prompt += "".join(f"- {q}\n" for q in brief["faq_questions"])
    if brief.get("type") == "update" and brief.get("existing_url"):
        prompt += (
            f"\nTHIS REPLACES a page already on the site ({brief['existing_url']}). "
            "Write it fresh around the sentence; the reader of the old page should still find their answer.\n"
        )
        if brief.get("existing_text"):
            prompt += f"\nCURRENT PAGE TEXT:\n{brief['existing_text']}\n"
    return prompt


def revision_prompt(brief: Dict[str, Any], draft: Dict[str, Any], problems: List[str]) -> str:
    faq = json.dumps(draft.get("faq") or [])
    bullets = "\n".join(f"- {p}" for p in problems)
    return f"""Fix only the problems listed below in this HogEye article. Keep everything else as written.

The article teaches this sentence:
{brief['reader_sentence']}

PROBLEMS:
{bullets}

How to fix them:
- Too long: cut the paragraphs the reader does not need to make the move. Do not shorten every sentence.
- Too short: answer the sections more fully using only the facts below. Never restate a step the article already gives.
- A sentence that states a rule (what the camera does not do, what HogEye is not, what the article covers): delete it. If the reader needs the point, show them doing the step instead.
- A repeated sentence or phrase: keep the first one and cut the others.
- A price or number not in the facts: delete it.
- Metadata: meta_title 60 characters or fewer and meta_description 160 or fewer, each with "{brief['target_keyword']}".

FACTS YOU MAY USE:
{_facts(brief)}

CURRENT META TITLE:
{draft.get('meta_title') or ''}

CURRENT META DESCRIPTION:
{draft.get('meta_description') or ''}

CURRENT EXCERPT:
{draft.get('excerpt') or ''}

CURRENT FAQ:
{faq}

CURRENT HTML:
{draft['html_content']}

Return the same JSON keys: html_content, meta_title, meta_description, excerpt, faq.
"""
