#!/usr/bin/env python3
"""
Suggest internal links using ONLY URLs from a sitemap inventory CSV (allowlist).

Reads Benchmark_Sitemap_Inventory.csv (url column) from scripts/seo/ttt_benchmark_sitemap_inventory.py,
sends article plain text + allowlist subset to OpenAI, prints suggested anchor phrases and URLs.
Does not modify files. Requires OPENAI_API_KEY in .env.

Usage:
  ./.venv/bin/python scripts/seo/hogeye_allowlisted_link_hints.py \\
    --inventory work/seo/benchmark/2026-01-01/Benchmark_Sitemap_Inventory.csv \\
    --article-md workspace/content_pipeline/monthly/2026-04/drafts/apr26_01_draft.md \\
    --max-allowlist 120
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv


def _load_urls(csv_path: Path, max_urls: int) -> List[str]:
    urls: List[str] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "url" not in (reader.fieldnames or []):
            raise SystemExit("CSV must have a 'url' column (Benchmark_Sitemap_Inventory.csv).")
        for row in reader:
            u = (row.get("url") or "").strip()
            if u:
                urls.append(u)
            if len(urls) >= max_urls:
                break
    return urls


def _plain_text(md: str) -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
    md = re.sub(r"^#+\s+.*$", "", md, flags=re.MULTILINE)
    md = re.sub(r"[`*_#]", "", md)
    return re.sub(r"\s+", " ", md).strip()[:12000]


def _default_chat_model() -> str:
    return (
        os.environ.get("OPENAI_MODEL", "").strip()
        or os.environ.get("OPENAI_NOTES_MODEL", "").strip()
        or "gpt-5.4-mini"
    )


def main() -> int:
    load_dotenv(Path.cwd() / ".env", override=False)

    ap = argparse.ArgumentParser(description="Allowlisted internal link hints (OpenAI)")
    ap.add_argument("--inventory", required=True, type=Path, help="Benchmark_Sitemap_Inventory.csv")
    ap.add_argument("--article-md", required=True, type=Path, help="Article markdown path")
    ap.add_argument("--max-allowlist", type=int, default=120, help="Max URLs from CSV to send")
    ap.add_argument(
        "--model",
        default=_default_chat_model(),
        help="Chat Completions model (default: OPENAI_MODEL, else OPENAI_NOTES_MODEL, else gpt-5.4-mini)",
    )
    args = ap.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Missing OPENAI_API_KEY in .env", file=sys.stderr)
        return 2

    urls = _load_urls(args.inventory, args.max_allowlist)
    if not urls:
        print("No URLs loaded from inventory.", file=sys.stderr)
        return 2

    body = _plain_text(args.article_md.read_text(encoding="utf-8"))
    system = (
        "You suggest internal links for SEO. You MUST only propose URLs from the allowlist provided. "
        "If no good fit exists, say so. Output JSON: {\"suggestions\": [{\"phrase\", \"url\", \"rationale\"}]} "
        "with at most 6 items. Never invent URLs."
    )
    user = (
        "Allowlist URLs (use only these):\n"
        + "\n".join(urls)
        + "\n\nArticle text:\n"
        + body
    )

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": args.model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=120,
    )
    if not r.ok:
        print(r.text, file=sys.stderr)
        return 2
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
