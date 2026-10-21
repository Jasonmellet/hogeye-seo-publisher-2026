#!/usr/bin/env python3
"""Run one approved HogEye brief through WRITING_LOOP.md phases 2 to 5, without touching the hub.

brief contract -> write (gpt-6-luna) -> local gate -> one writer fix pass on hard
failures -> second-provider check (Gemini) -> one fix pass on the checker's real
failures -> re-check -> local gate -> preview.

    ./.venv/bin/python scripts/seo/draft_piece.py \\
        workspace/content_pipeline/monthly/2026-10/briefs/oct26_01.json

Writes content/posts/<external_id>_wp_draft.json (the file push-content.mjs and the
WordPress publisher read) and <cycle>/review_packets/<external_id>__<slug>/article.html,
prints a one-line JSON summary, and exits non-zero when a human must look.
One brief per run. Do not loop this over a month.
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_draft_second_provider import check, gemini_key  # noqa: E402
from he_writer import Writer  # noqa: E402
from hogeye_content_quality import count_words, validate_item  # noqa: E402
from validate_he_briefs import validate_brief  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "content" / "posts"


def _faq_html(faq: List[Dict[str, str]]) -> str:
    if not faq:
        return ""
    items = "".join(
        f"<h3>{html.escape(f['question'])}</h3>\n<p>{html.escape(f['answer'])}</p>\n" for f in faq
    )
    return f"\n<h2>Frequently Asked Questions</h2>\n{items}"


def build_post(brief: Dict[str, Any], draft: Dict[str, Any], brief_path: Path) -> Dict[str, Any]:
    faq = draft.get("faq") or []
    post: Dict[str, Any] = {
        "externalId": brief["external_id"],
        "period": brief["period"],
        "title": brief["title"],
        "slug": brief["slug"],
        "content": draft["html_content"].strip() + _faq_html(faq),
        "status": "draft",
        "excerpt": (draft.get("excerpt") or draft.get("meta_description") or "").strip(),
        "meta_title": (draft.get("meta_title") or "").strip(),
        "meta_description": (draft.get("meta_description") or "").strip(),
        "focus_keyword": brief["target_keyword"],
        "categories": brief["categories"],
        "tags": brief.get("tags", []),
        "targetWordCount": brief["word_count"],
        "briefPath": str(brief_path.relative_to(REPO_ROOT)),
    }
    if brief.get("min_words"):
        post["minWords"] = brief["min_words"]
    if faq:
        post["faq_items"] = faq
    if brief.get("type") == "update":
        # A target for the WordPress step, not an opt-in to overwrite it.
        post["existing_url"] = brief["existing_url"]
    return post


def local_problems(post: Dict[str, Any]) -> List[str]:
    report = validate_item(post)
    problems = [e for e in report["errors"] if e != "output-hygiene findings present"]
    problems += [f"{f['label']}: \"{f['match']}\"" for f in report["findings"]]
    problems += report.get("warnings", [])
    for key, limit in (("meta_title", 60), ("meta_description", 160)):
        if len(post.get(key, "")) > limit:
            problems.append(f"{key} is {len(post[key])} characters; limit {limit}")
    return problems


def _preview(packet: Path, post: Dict[str, Any], model: str) -> None:
    result = post.get("secondProviderCheck", {})
    failures = "".join(
        f"<li>{html.escape(f.get('type', ''))}: {html.escape(f.get('quote', '')[:140])}</li>"
        for f in result.get("failures", [])
    )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(post['title'])}</title><style>
:root{{--bg:#f7f6f2;--fg:#1f2320;--muted:#5f665f;--accent:#2f6b3a;--card:#fff;--line:#dcdfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#171a18;--fg:#e8ebe6;--muted:#9aa39a;--accent:#8cc79a;--card:#202421;--line:#343a35}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:18px/1.65 Georgia,serif}} main{{max-width:680px;margin:0 auto;padding:32px 16px 64px}}
.meta{{font:14px/1.5 -apple-system,system-ui,sans-serif;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:28px;color:var(--muted)}}
.meta b{{color:var(--fg)}} h1{{font-size:34px;line-height:1.2;margin:0 0 18px}} h2{{font-size:24px;margin:32px 0 8px}} a{{color:var(--accent)}}
</style></head><body><main><div class="meta"><b>Draft for review, not in the hub.</b> {count_words(post['content'])} words.
Writer: {html.escape(model)}. Second-provider check: {html.escape(str(result.get('model', '-')))}, {html.escape(str(result.get('verdict', '-')))}.<br>
<b>Meta title:</b> {html.escape(post['meta_title'])}<br><b>Meta description:</b> {html.escape(post['meta_description'])}<br>
<b>URL:</b> hogeyecameras.com/{html.escape(post['slug'])}/ · <b>Hub row:</b> {html.escape(post['externalId'])}
{f'<br><b>Open check failures:</b><ul>{failures}</ul>' if failures else ''}</div>
<h1>{html.escape(post['title'])}</h1>
{post['content']}
</main></body></html>"""
    (packet / "article.html").write_text(page, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: draft_piece.py <brief.json>  (one brief per run)")
    brief_path = Path(sys.argv[1]).resolve()
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    contract = validate_brief(brief)
    if contract:
        print("Brief is not ready to draft:\n" + "\n".join(f"- {e}" for e in contract), file=sys.stderr)
        return 2

    api_key = gemini_key()
    writer = Writer()
    t0 = time.time()
    history: List[Dict[str, Any]] = []

    draft = writer.write(brief)
    post = build_post(brief, draft, brief_path)
    problems = local_problems(post)
    history.append({"step": "write", "words": count_words(post["content"]), "problems": problems})
    if problems:
        draft = writer.revise(brief, draft, problems)
        post = build_post(brief, draft, brief_path)
        problems = local_problems(post)
        history.append({"step": "local fix", "words": count_words(post["content"]), "problems": problems})

    result = check(post, brief, api_key)
    history.append({"step": "second-provider check", "verdict": result["verdict"], "failures": result.get("failures", [])})
    real = [f for f in result.get("failures", []) if f.get("quote_found")]
    if real:
        fixes = [
            f"{f['type']}: \"{f['quote']}\" ({f['why']}) Fix only this, by cutting or tightening; do not add a new copy of any step."
            for f in real
        ]
        draft = writer.revise(brief, draft, fixes)
        post = build_post(brief, draft, brief_path)
        result = check(post, brief, api_key)
        problems = local_problems(post)
        history.append({"step": "fix + re-check", "words": count_words(post["content"]), "verdict": result["verdict"],
                        "failures": result.get("failures", []), "problems": problems})

    post["secondProviderCheck"] = result
    post["generation"] = {"model": writer.model, "seconds": round(time.time() - t0, 1), "history": history}
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    post_path = POSTS_DIR / f"{brief['external_id']}_wp_draft.json"
    post_path.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    packet = brief_path.parent.parent / "review_packets" / f"{brief['external_id']}__{brief['slug']}"
    packet.mkdir(parents=True, exist_ok=True)
    _preview(packet, post, writer.model)

    final = validate_item(post)
    real_open = [f for f in result.get("failures", []) if f.get("quote_found")]
    summary = {
        "brief": brief["external_id"],
        "words": final["wordCount"],
        "range": [brief.get("min_words"), brief["word_count"]],
        "check": result["verdict"],
        "open_failures": [f"{f['type']}: {f.get('quote', '')[:80]}" for f in real_open],
        "local_gate": "pass" if final["ok"] else "fail",
        "local_problems": final["errors"] + [f"{f['label']}: {f['match']}" for f in final["findings"]],
        "warnings": final.get("warnings", []),
        "post": str(post_path.relative_to(REPO_ROOT)),
        "preview": str((packet / "article.html").relative_to(REPO_ROOT)),
    }
    print(json.dumps(summary))
    return 0 if final["ok"] and result["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
