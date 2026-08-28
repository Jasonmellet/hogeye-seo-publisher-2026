#!/usr/bin/env python3
"""
Dedicated AIOSEO optimization pass for WordPress posts.

Why:
- Run after draft publish to clean common AIOSEO red flags.
- Optionally uses an LLM for an intelligent whole-article pass.
- Can run on one post ID, many IDs, or recent posts by status.

By default this script is READ-ONLY (dry-run). Use --apply to write updates.
"""

from __future__ import annotations


def _publisher_bootstrap() -> None:
    import importlib.util
    from pathlib import Path

    p = Path(__file__).resolve()
    for c in p.parents:
        su = c / "scripts" / "publisher" / "site_setup.py"
        if su.is_file():
            spec = importlib.util.spec_from_file_location("_publisher_site_setup", su)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.ensure_publisher_paths()
            return
    raise RuntimeError("Could not find scripts/publisher/site_setup.py")


_publisher_bootstrap()

import argparse
import html
import json
import math
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from rich.console import Console
from rich.table import Table

from agt_publisher_core.client_config import load_client_config
from agt_publisher_core.config import Config
from agt_publisher_core.modules.auth import WordPressAuth
from agt_publisher_core.modules.wp_client import WordPressClient

console = Console()


@dataclass(frozen=True)
class AioseoAudit:
    keyword_in_seo_title: bool
    keyword_in_meta_description: bool
    keyword_in_intro: bool
    keyword_in_url: bool
    subheading_coverage_ratio: float
    subheading_total: int
    keyword_density_pct: float
    keyword_occurrences: int
    word_count: int


def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _strip_tags(s: str) -> str:
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<[^>]+>", " ", s)
    return _normalize_ws(html.unescape(s))


def _extract_first_paragraph_text(content_html: str) -> str:
    m = re.search(r"<p[^>]*>(.*?)</p>", content_html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return _strip_tags(m.group(1))


def _extract_h2_h3_texts(content_html: str) -> List[str]:
    out: List[str] = []
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h\1>", content_html, flags=re.IGNORECASE | re.DOTALL):
        out.append(_strip_tags(m.group(2)))
    return out


def _count_phrase(text: str, phrase: str) -> int:
    if not phrase.strip():
        return 0
    # Treat phrase as exact token sequence with word boundaries.
    pattern = re.compile(rf"(?<!\w){re.escape(phrase.strip())}(?!\w)", flags=re.IGNORECASE)
    return len(pattern.findall(text))


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").strip().lower())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def _slug_contains_keyword(slug: str, focus_keyword: str) -> bool:
    ks = _slugify(focus_keyword)
    ss = _slugify(slug)
    return bool(ks and ks in ss)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _aioseo_audit(*, content_html: str, seo_title: str, meta_description: str, focus_keyword: str, slug: str) -> AioseoAudit:
    full_text = _strip_tags(content_html)
    words = _word_count(full_text)
    occ = _count_phrase(full_text, focus_keyword)
    density = (occ / max(1, words)) * 100.0

    intro = _extract_first_paragraph_text(content_html)
    headings = _extract_h2_h3_texts(content_html)
    heading_hits = sum(1 for h in headings if _count_phrase(h, focus_keyword) > 0)
    heading_ratio = (heading_hits / len(headings)) if headings else 0.0

    return AioseoAudit(
        keyword_in_seo_title=_count_phrase(seo_title, focus_keyword) > 0,
        keyword_in_meta_description=_count_phrase(meta_description, focus_keyword) > 0,
        keyword_in_intro=_count_phrase(intro, focus_keyword) > 0,
        keyword_in_url=_count_phrase((slug or "").replace("-", " "), focus_keyword) > 0,
        subheading_coverage_ratio=heading_ratio,
        subheading_total=len(headings),
        keyword_density_pct=density,
        keyword_occurrences=occ,
        word_count=words,
    )


def _merge_aioseo_meta(existing: Dict[str, Any], *, seo_title: str, meta_description: str, focus_keyword: str) -> Dict[str, Any]:
    out = dict(existing or {})
    out["title"] = seo_title
    out["description"] = meta_description
    kp = out.get("keyphrases")
    if not isinstance(kp, dict):
        kp = {}
    focus = kp.get("focus")
    if not isinstance(focus, dict):
        focus = {}
    focus["keyphrase"] = focus_keyword
    kp["focus"] = focus
    out["keyphrases"] = kp
    return out


def _extract_json_object(s: str) -> Dict[str, Any]:
    s = (s or "").strip()
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in model output.")
    obj = json.loads(m.group(0))
    if not isinstance(obj, dict):
        raise ValueError("Model output JSON is not an object.")
    return obj


def _openai_optimize(
    *,
    api_key: str,
    model: str,
    focus_keyword: str,
    post_title: str,
    slug: str,
    seo_title: str,
    meta_description: str,
    content_html: str,
    max_content_chars: int,
) -> Dict[str, str]:
    trimmed_html = content_html[:max_content_chars]
    system = (
        "You are a senior WordPress AIOSEO editor. "
        "Revise content and metadata to improve AIOSEO checks without changing factual meaning. "
        "Do not invent claims, numbers, or sources. Keep all existing links unless clearly broken."
    )
    user = (
        "Optimize this post for the exact focus keyword.\n\n"
        f"Focus keyword: {focus_keyword}\n"
        f"Post title: {post_title}\n"
        f"Slug: {slug}\n"
        f"Current SEO title: {seo_title}\n"
        f"Current meta description: {meta_description}\n\n"
        "Target outcomes:\n"
        "- Focus keyword appears in SEO title.\n"
        "- Focus keyword appears in meta description.\n"
        "- Focus keyword appears in first paragraph.\n"
        "- At least ~30% of H2/H3 headings reflect the focus keyword naturally.\n"
        "- Improve keyword density toward ~0.5%+ naturally (no obvious stuffing).\n"
        "- Preserve readability and human tone.\n"
        "- Keep HTML structure valid and preserve links.\n\n"
        "Return JSON only with keys:\n"
        "{\n"
        '  "seo_title": "...",\n'
        '  "meta_description": "...",\n'
        '  "content_html": "..." \n'
        "}\n\n"
        f"Content HTML:\n{trimmed_html}"
    )

    payload = json.dumps(
        {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = str(data["choices"][0]["message"]["content"] or "").strip()
    obj = _extract_json_object(content)
    return {
        "seo_title": _normalize_ws(str(obj.get("seo_title") or seo_title)),
        "meta_description": _normalize_ws(str(obj.get("meta_description") or meta_description)),
        "content_html": str(obj.get("content_html") or content_html),
    }


def _ensure_intro_contains_keyword(content_html: str, focus_keyword: str) -> str:
    if _count_phrase(_extract_first_paragraph_text(content_html), focus_keyword) > 0:
        return content_html
    m = re.search(r"(<p[^>]*>)(.*?)(</p>)", content_html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return content_html
    insert = f" {focus_keyword} is central to this guide."
    new_mid = m.group(2) + insert
    return content_html[: m.start()] + m.group(1) + new_mid + m.group(3) + content_html[m.end() :]


def _ensure_subheading_coverage(content_html: str, focus_keyword: str, min_ratio: float = 0.30) -> str:
    pattern = re.compile(r"<h([23])([^>]*)>(.*?)</h\1>", flags=re.IGNORECASE | re.DOTALL)
    matches = list(pattern.finditer(content_html))
    if not matches:
        return content_html
    total = len(matches)
    hits = sum(1 for m in matches if _count_phrase(_strip_tags(m.group(3)), focus_keyword) > 0)
    target = int(math.ceil(total * min_ratio))
    needed = max(0, target - hits)
    if needed <= 0:
        return content_html

    def _repl(m: re.Match[str]) -> str:
        nonlocal needed
        lvl = m.group(1)
        attrs = m.group(2)
        inner = m.group(3)
        if needed <= 0:
            return m.group(0)
        if _count_phrase(_strip_tags(inner), focus_keyword) > 0:
            return m.group(0)
        needed -= 1
        return f"<h{lvl}{attrs}>{inner} ({focus_keyword})</h{lvl}>"

    return pattern.sub(_repl, content_html)


def _ensure_core_flags(*, seo_title: str, meta_description: str, content_html: str, focus_keyword: str) -> Dict[str, str]:
    out_title = seo_title
    out_meta = meta_description
    out_html = content_html

    if _count_phrase(out_title, focus_keyword) == 0:
        out_title = _normalize_ws(f"{focus_keyword}: {out_title}")
    if _count_phrase(out_meta, focus_keyword) == 0:
        out_meta = _normalize_ws(f"{focus_keyword}. {out_meta}")
    out_html = _ensure_intro_contains_keyword(out_html, focus_keyword)
    out_html = _ensure_subheading_coverage(out_html, focus_keyword, min_ratio=0.30)
    return {"seo_title": out_title, "meta_description": out_meta, "content_html": out_html}


def _parse_ids_csv(raw: str) -> List[int]:
    out: List[int] = []
    for part in (raw or "").split(","):
        p = part.strip()
        if not p:
            continue
        out.append(int(p))
    return out


def _collect_recent_post_ids(wp: WordPressClient, *, statuses: Set[str], limit: int) -> List[int]:
    ids: List[int] = []
    page = 1
    per_page = min(100, max(1, limit))
    while len(ids) < limit:
        r = wp.get_json(
            "posts",
            params={"context": "edit", "status": "any", "orderby": "modified", "order": "desc", "per_page": per_page, "page": page},
        )
        if not r.ok or not isinstance(r.data, list) or not r.data:
            break
        for row in r.data:
            st = str(row.get("status") or "").strip().lower()
            if statuses and st not in statuses:
                continue
            pid = int(row.get("id") or 0)
            if pid:
                ids.append(pid)
            if len(ids) >= limit:
                break
        page += 1
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description="Dedicated AIOSEO optimization pass for WordPress posts")
    ap.add_argument("--post-ids", default="", help="Comma-separated WP post IDs to optimize")
    ap.add_argument("--statuses", default="draft", help="CSV statuses when auto-selecting recent posts (default: draft)")
    ap.add_argument("--limit", type=int, default=10, help="Recent post limit when --post-ids is empty")
    ap.add_argument("--model", default=(os.getenv("OPENAI_MODEL") or "gpt-4o-mini"), help="OpenAI model for LLM pass")
    ap.add_argument("--focus-keyword", default="", help="Optional override focus keyword for all selected posts")
    ap.add_argument("--max-content-chars", type=int, default=90000, help="Max HTML chars sent to LLM")
    ap.add_argument("--no-llm", action="store_true", help="Skip LLM and only apply deterministic fixes")
    ap.add_argument("--apply", action="store_true", help="Write updates to WordPress (default is dry-run)")
    args = ap.parse_args()

    Config.validate()
    client = load_client_config()
    if (client.seoPlugin or "").strip().lower() != "aioseo":
        console.print("[yellow]Warning:[/yellow] client.config seoPlugin is not aioseo; this script is tuned for AIOSEO.")

    auth = WordPressAuth()
    ok, msg, _ = auth.test_connection()
    if not ok:
        console.print(f"[red]Connection failed:[/red] {msg}")
        return 2

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not args.no_llm and not api_key:
        console.print("[red]OPENAI_API_KEY is required unless --no-llm is set.[/red]")
        return 2

    wp = WordPressClient(auth.get_session())

    ids = _parse_ids_csv(args.post_ids)
    if not ids:
        statuses = {s.strip().lower() for s in args.statuses.split(",") if s.strip()}
        ids = _collect_recent_post_ids(wp, statuses=statuses, limit=max(1, args.limit))

    if not ids:
        console.print("[yellow]No posts selected.[/yellow]")
        return 0

    console.print(f"[cyan]Selected {len(ids)} post(s). Apply mode:[/cyan] {args.apply}")

    table = Table(show_header=True)
    table.add_column("Post ID")
    table.add_column("Status")
    table.add_column("Keyword")
    table.add_column("Before")
    table.add_column("After")
    table.add_column("Action")

    updated = 0
    failures = 0

    for pid in ids:
        row_status = "ok"
        action = "dry-run"
        try:
            got = wp.get_json(f"posts/{pid}", params={"context": "edit"})
            if not got.ok or not isinstance(got.data, dict):
                raise RuntimeError(f"Could not load post {pid} (HTTP {got.status_code}).")
            post = got.data
            status = str(post.get("status") or "")
            slug = str(post.get("slug") or "")
            title = str((post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered") or "")
            content_html = str((post.get("content") or {}).get("raw") or "")
            if not content_html:
                content_html = str((post.get("content") or {}).get("rendered") or "")

            aio = post.get("aioseo_meta_data")
            aio = dict(aio) if isinstance(aio, dict) else {}
            seo_title = _normalize_ws(str(aio.get("title") or title))
            meta_description = _normalize_ws(str(aio.get("description") or (post.get("excerpt") or {}).get("raw") or ""))

            focus_keyword = _normalize_ws(args.focus_keyword)
            if not focus_keyword:
                kps = aio.get("keyphrases")
                if isinstance(kps, dict):
                    focus = kps.get("focus")
                    if isinstance(focus, dict):
                        focus_keyword = _normalize_ws(str(focus.get("keyphrase") or ""))
            if not focus_keyword:
                raise RuntimeError("Missing focus keyword (pass --focus-keyword or set AIOSEO focus keyphrase first).")

            before = _aioseo_audit(
                content_html=content_html,
                seo_title=seo_title,
                meta_description=meta_description,
                focus_keyword=focus_keyword,
                slug=slug,
            )

            candidate = {"seo_title": seo_title, "meta_description": meta_description, "content_html": content_html}
            if not args.no_llm:
                candidate = _openai_optimize(
                    api_key=api_key,
                    model=args.model,
                    focus_keyword=focus_keyword,
                    post_title=title,
                    slug=slug,
                    seo_title=seo_title,
                    meta_description=meta_description,
                    content_html=content_html,
                    max_content_chars=max(1000, args.max_content_chars),
                )

            fixed = _ensure_core_flags(
                seo_title=candidate["seo_title"],
                meta_description=candidate["meta_description"],
                content_html=candidate["content_html"],
                focus_keyword=focus_keyword,
            )

            candidate_slug = slug
            if status.lower() == "draft" and not _slug_contains_keyword(slug, focus_keyword):
                kw_slug = _slugify(focus_keyword)
                if kw_slug:
                    if slug:
                        candidate_slug = f"{kw_slug}-{slug}"
                    else:
                        candidate_slug = kw_slug
                    candidate_slug = _slugify(candidate_slug)[:190].strip("-")

            after = _aioseo_audit(
                content_html=fixed["content_html"],
                seo_title=fixed["seo_title"],
                meta_description=fixed["meta_description"],
                focus_keyword=focus_keyword,
                slug=candidate_slug,
            )

            before_flags = f"title:{'Y' if before.keyword_in_seo_title else 'N'} meta:{'Y' if before.keyword_in_meta_description else 'N'} intro:{'Y' if before.keyword_in_intro else 'N'} url:{'Y' if before.keyword_in_url else 'N'} dens:{before.keyword_density_pct:.2f}%"
            after_flags = f"title:{'Y' if after.keyword_in_seo_title else 'N'} meta:{'Y' if after.keyword_in_meta_description else 'N'} intro:{'Y' if after.keyword_in_intro else 'N'} url:{'Y' if after.keyword_in_url else 'N'} dens:{after.keyword_density_pct:.2f}%"

            if args.apply:
                merged_aioseo = _merge_aioseo_meta(
                    aio,
                    seo_title=fixed["seo_title"],
                    meta_description=fixed["meta_description"],
                    focus_keyword=focus_keyword,
                )
                payload = {"content": fixed["content_html"], "aioseo_meta_data": merged_aioseo}
                if candidate_slug and candidate_slug != slug and status.lower() == "draft":
                    payload["slug"] = candidate_slug
                upd = wp.post_json(f"posts/{pid}", payload, params={"context": "edit"})
                if not upd.ok:
                    raise RuntimeError(f"Update failed (HTTP {upd.status_code})")
                action = "updated"
                if payload.get("slug"):
                    action += " +slug"
                updated += 1
        except Exception as e:
            row_status = "error"
            action = f"failed: {e}"
            failures += 1
            status = "-"
            focus_keyword = "-"
            before_flags = "-"
            after_flags = "-"

        table.add_row(str(pid), status, focus_keyword, before_flags, after_flags, action)

    console.print(table)
    if args.apply:
        console.print(f"[green]Updated:[/green] {updated}  [red]Failures:[/red] {failures}")
    else:
        console.print(f"[cyan]Dry-run complete.[/cyan] Failures: {failures}")

    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

