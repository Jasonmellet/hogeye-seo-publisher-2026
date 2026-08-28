#!/usr/bin/env python3
"""
Convert an approved monthly draft markdown (`<article_id>_draft.md`) into a JSON post file for publish_content_item.py.

Expects either:
- **YAML frontmatter** (`---` … `---`) with `title`, `slug`, `meta_title`, `meta_description`, `focus_keyword`, `categories`, optional `excerpt`, then `# Article title` and body; or
- **Legacy bullet metadata**: SEO Metadata list, ## Metadata list, then `# Draft:` / `# Article title` and body.
Strips HTML comment blocks and optional ## Claims audit notes (and following) for the WordPress body.
Does not put the article H1 into the HTML body (theme shows post title). Normalizes outline labels like `## H2: ...` → `## ...` and `## H3: ...` under FAQ → `### ...`, and drops a standalone `## Main sections` line.

Usage:
  ./.venv/bin/python scripts/seo/hogeye_draft_md_to_post_json.py \\
    output/drafts/2026-04/drafts/apr26_01_draft.md \\
    --output output/wordpress/posts/apr26_01_wp_draft.json

Categories and tags (SEO decision — no generic defaults):
  - Optional site-wide defaults in `PROJECT_CONFIG.json` → `wordpress.default_post_*` only after taxonomy is agreed.
  - Per-article in markdown: `- categories: …` (required unless defaults are set) and `- tags: …` (optional); comma, semicolon, or |.
  - At least one category is required after merge (defaults + draft), or the script exits with an error.

Then:
  ./.venv/bin/python scripts/publisher/publish_content_item.py output/wordpress/posts/apr26_01_wp_draft.json --type posts --status draft
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import markdown

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from repo_workspace import workspace_dir_under, workspace_rel_posix


def _split_yaml_frontmatter(raw: str) -> Tuple[str, Dict[str, Any]]:
    """If file starts with --- YAML ---, return (body_after, frontmatter dict)."""
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", raw, re.DOTALL)
    if not m:
        return raw, {}
    if yaml is None:
        print("Warning: PyYAML not installed; install requirements.txt — YAML frontmatter ignored.", file=sys.stderr)
        return raw, {}
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        print(f"Warning: YAML frontmatter parse failed ({e}); continuing without it.", file=sys.stderr)
        return raw, {}
    if not isinstance(fm, dict):
        return raw, {}
    rest = raw[m.end() :]
    return rest, fm


def _yaml_dict_to_kv(yd: Dict[str, Any]) -> Dict[str, str]:
    """Map YAML frontmatter keys to internal kv used by this script."""
    kv: Dict[str, str] = {}
    t = yd.get("title")
    mt = yd.get("meta_title") or yd.get("seo_title")
    if mt:
        kv["seo_title"] = str(mt).strip()
    elif t:
        kv["seo_title"] = str(t).strip()
    if yd.get("meta_description"):
        kv["meta_description"] = str(yd["meta_description"]).strip()
    fk = yd.get("focus_keyword") or yd.get("primary_keyword")
    if fk:
        kv["primary_keyword"] = str(fk).strip()
    if yd.get("slug"):
        kv["slug"] = str(yd["slug"]).strip().strip('"').strip("'")
    # Stable dashboard identity, independent of the slug (slug is an SEO field that
    # can change). Set once in frontmatter and never changed.
    eid = yd.get("external_id") or yd.get("externalId")
    if eid:
        kv["external_id"] = str(eid).strip().strip('"').strip("'")
    cats = yd.get("categories")
    if isinstance(cats, list):
        kv["categories"] = ", ".join(str(c).strip() for c in cats if c)
    elif cats:
        kv["categories"] = str(cats).strip()
    tags = yd.get("tags")
    if isinstance(tags, list):
        kv["tags"] = ", ".join(str(t).strip() for t in tags if t)
    elif tags:
        kv["tags"] = str(tags).strip()
    if yd.get("excerpt"):
        kv["excerpt"] = str(yd["excerpt"]).strip()
    return kv


def _load_wp_taxonomy_defaults(project_root: Path) -> Tuple[List[str], List[str]]:
    """Read default post categories/tags from HogEye PROJECT_CONFIG.json."""
    cfg_path = workspace_dir_under(project_root.resolve()) / "PROJECT_CONFIG.json"
    if not cfg_path.exists():
        return [], []
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    wp = data.get("wordpress") if isinstance(data.get("wordpress"), dict) else {}
    cats = wp.get("default_post_categories") or []
    tags = wp.get("default_post_tags") or []
    out_c = [str(x).strip() for x in cats if str(x).strip()]
    out_t = [str(x).strip() for x in tags if str(x).strip()]
    return out_c, out_t


def _split_taxonomy_value(val: str) -> List[str]:
    """Split '- categories: a, b; c' style values."""
    if not val or not str(val).strip():
        return []
    parts = re.split(r"[,;|]", str(val))
    return [p.strip() for p in parts if p.strip()]


def _dedupe_preserve(seq: List[str]) -> List[str]:
    return list(dict.fromkeys(seq))


def _strip_comment_blocks(text: str) -> str:
    """Remove <!-- ... --> including multiline comments."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip() + "\n"


def _parse_kv_bullets(text: str) -> Dict[str, str]:
    """Parse lines like '- key: value' anywhere in file (first occurrence wins)."""
    data: Dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^[-*]\s+([^:]+):\s*(.*)$", line.strip())
        if not m:
            continue
        key = m.group(1).strip().lower().replace(" ", "_")
        val = m.group(2).strip()
        if key not in data:
            data[key] = val
    return data


def _find_article_title_and_body(md: str) -> Tuple[str, str]:
    """
    Title: first markdown H1 whose text does not start with 'Draft:' (skip '# Draft: id' scaffolding).
    Body: from that line through end, then strip claims audit.
    """
    lines = md.splitlines()
    title_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if not line.startswith("# "):
            continue
        rest = line[2:].strip()
        if rest.lower().startswith("draft:"):
            continue
        title_idx = i
        break
    if title_idx is None:
        raise ValueError("Could not find article H1 (expected '# Title' after optional '# Draft: …').")

    title = lines[title_idx][2:].strip()
    # Body excludes the article H1 line — WordPress shows `title` in the template; body should not duplicate an <h1>.
    body_lines = lines[title_idx + 1 :]

    # Remove trailing claims audit section
    cut = len(body_lines)
    for i, line in enumerate(body_lines):
        if line.strip().lower().startswith("## claims audit"):
            cut = i
            break
    body_md = "\n".join(body_lines[:cut]).strip() + "\n"
    return title, body_md


def _normalize_outline_headings(body_md: str) -> str:
    """
    Strip editorial scaffolding from monthly drafts: literal 'H2:'/'H3:' labels, 'Main sections', etc.
    """
    out_lines: List[str] = []
    for line in body_md.splitlines():
        s = line.strip()
        if s.lower() in ("## main sections", "## main section"):
            continue
        m2 = re.match(r"^##\s+H2:\s*(.*)$", line)
        if m2:
            out_lines.append(f"## {m2.group(1).strip()}")
            continue
        m3 = re.match(r"^##\s+H3:\s*(.*)$", line)
        if m3:
            out_lines.append(f"### {m3.group(1).strip()}")
            continue
        out_lines.append(line)
    return "\n".join(out_lines).strip() + "\n"


def _parse_faq_items_from_body_md(body_md: str) -> List[Dict[str, str]]:
    """
    Parse FAQ section into AIOSEO-ready faq_items.

    Supports:
    - ## Frequently Asked Questions | ## FAQ
    - ### Question (answer on following lines)
    - **Question** (answer on following lines; May 2026 drafts)
    - Ends at next ## heading, a horizontal rule (---), or end of file.
    """
    lines = body_md.splitlines()
    in_faq = False
    items: List[Dict[str, str]] = []
    current_q: Optional[str] = None
    current_a: List[str] = []

    def flush() -> None:
        nonlocal current_q, current_a
        if current_q is None:
            return
        ans = " ".join(x.strip() for x in current_a if x.strip()).strip()
        if current_q and ans:
            items.append({"question": current_q.strip(), "answer": ans})
        current_q = None
        current_a = []

    def is_faq_heading(heading: str) -> bool:
        h = heading.strip().lower()
        if h == "faq":
            return True
        return bool(re.search(r"frequently\s+asked\s+questions", heading, flags=re.I))

    for line in lines:
        s = line.strip()
        if re.match(r"^[\s]*-{3,}[\s]*$", line) or re.match(r"^[\s]*\*{3,}[\s]*$", line):
            if in_faq:
                flush()
                break
            continue
        if s.startswith("## ") and not s.startswith("### "):
            heading = s[3:].strip()
            if is_faq_heading(heading):
                in_faq = True
                flush()
                continue
            if in_faq:
                flush()
                break
        if not in_faq:
            continue
        m = re.match(r"^###\s+(.+)$", line)
        if m:
            flush()
            current_q = m.group(1).strip()
            current_a = []
            continue
        m_bold = re.match(r"^\*\*(.+?)\*\*\s*$", s)
        if m_bold:
            flush()
            current_q = m_bold.group(1).strip()
            current_a = []
            continue
        if current_q is not None and s:
            current_a.append(s)
    flush()
    return items


def _slugify(s: str, max_len: int = 80) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s[:max_len].rstrip("-")


def _first_paragraph_excerpt(md: str, max_chars: int = 240) -> str:
    text = re.sub(r"<[^>]+>", " ", markdown.markdown(md))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rsplit(" ", 1)[0] + "…"


def main() -> int:
    ap = argparse.ArgumentParser(description="Monthly draft markdown → publish JSON")
    ap.add_argument("draft_md", help="Path to <article_id>_draft.md (under monthly/.../drafts/)")
    ap.add_argument("--output", "-o", required=True, help="Write JSON here (e.g. content/posts/slug.json)")
    ap.add_argument("--slug", default="", help="Override slug (default: slugified title)")
    ap.add_argument("--keep-claims-audit", action="store_true", help="Include claims audit section in body")
    ap.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root (for PROJECT_CONFIG.json taxonomy defaults)",
    )
    args = ap.parse_args()

    src = Path(args.draft_md)
    raw = src.read_text(encoding="utf-8")

    body_wo_fm, yaml_fm = _split_yaml_frontmatter(raw)
    text_for_kv = body_wo_fm if yaml_fm else raw
    kv_yaml = _yaml_dict_to_kv(yaml_fm) if yaml_fm else {}
    kv_bullets = _parse_kv_bullets(text_for_kv)
    kv = {**kv_yaml, **kv_bullets}

    cleaned = _strip_comment_blocks(text_for_kv)

    if not args.keep_claims_audit:
        # Re-apply claims strip on cleaned text
        lines = cleaned.splitlines()
        cut = len(lines)
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("## claims audit"):
                cut = i
                break
        cleaned = "\n".join(lines[:cut]).strip() + "\n"

    title, body_md = _find_article_title_and_body(cleaned)
    body_md = _normalize_outline_headings(body_md)

    seo_title = kv.get("seo_title") or title
    meta_description = kv.get("meta_description") or ""
    focus = kv.get("primary_keyword") or ""

    slug = (args.slug or "").strip() or (kv.get("slug") or "").strip() or _slugify(title)
    excerpt = (kv.get("excerpt") or "").strip() or meta_description or _first_paragraph_excerpt(body_md)

    faq_items = _parse_faq_items_from_body_md(body_md)

    html = markdown.markdown(body_md, extensions=["extra", "nl2br"])

    default_cats, default_tags = _load_wp_taxonomy_defaults(args.project_root.resolve())
    extra_cats = _split_taxonomy_value(kv.get("categories", ""))
    extra_tags = _split_taxonomy_value(kv.get("tags", ""))
    categories = _dedupe_preserve(list(default_cats) + extra_cats)
    tags = _dedupe_preserve(list(default_tags) + extra_tags)
    if not categories:
        print(
            "Error: no categories assigned. The SEO/content owner must choose categories that match "
            "your live WordPress taxonomy: set `wordpress.default_post_categories` in "
            f"{workspace_rel_posix()}/PROJECT_CONFIG.json and/or add a line like "
            "`- categories: Category Name` to this draft (see content_pipeline/WORKFLOW.md).",
            file=sys.stderr,
        )
        return 2

    out_obj: Dict[str, Any] = {}
    external_id = (kv.get("external_id") or "").strip()
    if external_id:
        # Permanent identity used by the dashboard ingest (push-content.mjs). Stays
        # the same even if `slug` changes, so a slug edit never orphans the post.
        out_obj["externalId"] = external_id
    out_obj.update({
        "title": seo_title,
        "slug": slug,
        "content": html,
        "status": "draft",
        "excerpt": excerpt,
        "meta_title": seo_title,
        "meta_description": meta_description,
        "focus_keyword": focus,
        "categories": categories,
        "tags": tags,
    })
    if faq_items:
        out_obj["faq_items"] = faq_items

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(2)
