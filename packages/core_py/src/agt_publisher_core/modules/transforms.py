"""
HTML transforms used across publishing scripts.

Design goals:
- Idempotent (safe to re-run)
- Avoid Gutenberg block breakage (e.g., malformed duplicate style attrs)
- Provide consistent spacing in rendered content
"""

from __future__ import annotations

import re
from typing import List, Tuple

P_STYLE = "margin-bottom: 1.5rem; line-height: 1.7;"
H2_STYLE = "margin-top: 2.5rem; margin-bottom: 1.5rem; line-height: 1.3;"
H3_STYLE = "margin-top: 2rem; margin-bottom: 1rem; line-height: 1.4;"
LI_STYLE = "margin-bottom: 0.5rem;"


def fix_malformed_h2_styles(content: str) -> str:
    """
    Fix cases like: <h2 style="...; style="..."> which break Gutenberg.
    """

    def _fix(match: re.Match) -> str:
        tag = match.group(0)
        # collapse duplicate style=" occurrences inside the same tag
        tag = re.sub(r'style="([^"]*)"\s+style="([^"]*)"', r'style="\1 \2"', tag)
        return tag

    return re.sub(r"<h2[^>]*>", _fix, content)


def add_spacing_to_html(content: str) -> str:
    """
    Add spacing styles to <p>, <h2>, <h3>, <li> when missing.
    Idempotent: does not override tags that already have style=.
    """
    # Paragraphs
    content = re.sub(
        r"<p(?![^>]*\sstyle=)([^>]*)>",
        rf'<p\1 style="{P_STYLE}">',
        content,
        flags=re.IGNORECASE,
    )
    # H2
    content = re.sub(
        r"<h2(?![^>]*\sstyle=)([^>]*)>",
        rf'<h2\1 style="{H2_STYLE}">',
        content,
        flags=re.IGNORECASE,
    )
    # H3
    content = re.sub(
        r"<h3(?![^>]*\sstyle=)([^>]*)>",
        rf'<h3\1 style="{H3_STYLE}">',
        content,
        flags=re.IGNORECASE,
    )
    # LI
    content = re.sub(
        r"<li(?![^>]*\sstyle=)([^>]*)>",
        rf'<li\1 style="{LI_STYLE}">',
        content,
        flags=re.IGNORECASE,
    )

    return content


def normalize_whitespace(content: str) -> str:
    # Collapse excessive blank lines (but keep intentional separation)
    return re.sub(r"\n{4,}", "\n\n", content)


def remove_all_tocs(content: str) -> str:
    """
    Remove TOC blocks created by our scripts or manual inserts.
    Designed to be aggressive but limited to common TOC containers.
    """
    # Remove common TOC container divs
    content = re.sub(
        r'<div[^>]*class="[^"]*table-of-contents[^"]*"[^>]*>.*?</div>\s*</div>',
        "",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    content = re.sub(
        r'<div[^>]*class="[^"]*table-of-contents[^"]*"[^>]*>.*?</div>',
        "",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Remove TOC headings with immediate list (light heuristic)
    content = re.sub(
        r"<h2[^>]*>\s*Table of Contents\s*</h2>\s*(<ul[^>]*>.*?</ul>)",
        "",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return content


def ensure_unique_heading_ids(content: str) -> Tuple[str, int]:
    """
    Ensure each H2 has an id= attribute.
    Returns (updated_content, count_added).
    """

    def slugify(text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text).strip("-")
        return text or "section"

    used_ids = set(re.findall(r'id="([^"]+)"', content))
    added = 0

    def repl(match: re.Match) -> str:
        nonlocal added, used_ids
        attrs = match.group(1) or ""
        inner = match.group(2) or ""
        if re.search(r'\sid="[^"]+"', attrs):
            return match.group(0)

        base = slugify(inner)
        candidate = base
        n = 2
        while candidate in used_ids:
            candidate = f"{base}-{n}"
            n += 1
        used_ids.add(candidate)
        added += 1
        return f'<h2{attrs} id="{candidate}">{inner}</h2>'

    updated = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, content, flags=re.IGNORECASE | re.DOTALL)
    return updated, added


def insert_toc_after_intro(content: str) -> Tuple[str, int]:
    """
    Insert a single TOC after the second paragraph using existing H2s as entries.
    Returns (updated_content, toc_items_count).
    """
    # Find H2 headings (exclude FAQ)
    h2s: List[Tuple[str, str]] = []
    for m in re.finditer(r'<h2([^>]*)\sid="([^"]+)"[^>]*>(.*?)</h2>', content, flags=re.IGNORECASE | re.DOTALL):
        hid = m.group(2)
        title = re.sub(r"<[^>]+>", "", m.group(3)).strip()
        if title.lower().startswith("frequently asked"):
            continue
        h2s.append((hid, title))

    if not h2s:
        return content, 0

    toc_items = "\n".join([f'<li style="{LI_STYLE}"><a href="#{hid}">{title}</a></li>' for hid, title in h2s])
    toc_html = f'''<div class="table-of-contents" style="background-color: #f9f9f9; padding: 2rem; margin: 2rem 0; border-left: 4px solid #0066cc; border-radius: 8px;">
<h3 style="margin-top: 0; margin-bottom: 1rem;">Table of Contents</h3>
<ul style="margin: 0; padding-left: 1.25rem;">
{toc_items}
</ul>
</div>'''

    paras = list(re.finditer(r"(<p[^>]*>.*?</p>)", content, flags=re.IGNORECASE | re.DOTALL))
    if len(paras) >= 2:
        insert_pos = paras[1].end()
        updated = content[:insert_pos] + "\n\n" + toc_html + "\n\n" + content[insert_pos:]
        return updated, len(h2s)

    return content + "\n\n" + toc_html, len(h2s)

