"""
ACF block builders for the Camp Lakota theme.

These blocks replicate the structure used by the "Our Story" interior pages.
Centralizing these prevents drift across one-off scripts.
"""

from __future__ import annotations

import json
import re
from typing import List


def html_to_acf_content_block(html_content: str, padding_top: str = "pt-4", padding_bottom: str = "pb-4") -> str:
    escaped_content = json.dumps(html_content)[1:-1]  # remove outer quotes
    return (
        f'<!-- wp:camplakota/content {{"name":"camplakota/content","data":{{'
        f'"content":"{escaped_content}","_content":"field_6614a1b785f52",'
        f'"padding_top":"{padding_top}","_padding_top":"field_6614a581b0eea",'
        f'"padding_bottom":"{padding_bottom}","_padding_bottom":"field_6614a5d6b0eeb"'
        f'}},"mode":"edit"}} /-->'
    )


def create_clearfix_block() -> str:
    """
    Some theme blocks (notably image columns) can use floats. To prevent the following
    content from wrapping around images, insert a minimal clearfix block.
    """
    return html_to_acf_content_block('<div style="clear:both;"></div>', padding_top="pt-0", padding_bottom="pb-0")


def create_large_image_block(image_id: int, padding_top: str = "pt-4", padding_bottom: str = "pb-4", max_height: str = "500") -> str:
    return (
        f'<!-- wp:camplakota/large-image {{"name":"camplakota/large-image","data":{{'
        f'"image":{image_id},"_image":"field_6614ac8a8d6df",'
        f'"padding_top":"{padding_top}","_padding_top":"field_6614a6e9e8ae6",'
        f'"padding_bottom":"{padding_bottom}","_padding_bottom":"field_6614a6e9e8ae9",'
        f'"max_height":"{max_height}","_max_height":"field_661829c0ae3be"'
        f'}},"mode":"edit"}} /-->'
    )


def create_two_column_images_block(
    image_id_1: int,
    image_id_2: int,
    padding_top: str = "pt-0",
    padding_bottom: str = "pb-0",
    max_height: str = "500",
) -> str:
    return (
        f'<!-- wp:camplakota/two-column-images {{"name":"camplakota/two-column-images","data":{{'
        f'"images_0_image":{image_id_1},"_images_0_image":"field_66184d55d83dd",'
        f'"images_1_image":{image_id_2},"_images_1_image":"field_66184d55d83dd",'
        f'"images":2,"_images":"field_66184d19d83dc",'
        f'"max_height":"{max_height}","_max_height":"field_661851eaa863b",'
        f'"padding_top":"{padding_top}","_padding_top":"field_6618529ec9efc",'
        f'"padding_bottom":"{padding_bottom}","_padding_bottom":"field_661852fbaeba5"'
        f'}},"mode":"edit"}} /-->'
    )


def split_content_by_h2(html_content: str) -> List[str]:
    """
    Split content by H2 headings, preserving each section. Safe for JSON-escaped strings.
    """
    content = html_content.replace("\\n", "\n").replace('\\"', '"').replace("\\/", "/").replace("&amp;", "&")
    h2_pattern = r"(<h2[^>]*>.*?</h2>)"
    h2_matches = list(re.finditer(h2_pattern, content, re.DOTALL | re.IGNORECASE))
    if not h2_matches:
        return [content.strip()] if content.strip() else []

    sections: List[str] = []
    if h2_matches[0].start() > 0:
        intro = content[: h2_matches[0].start()].strip()
        if intro:
            sections.append(intro)

    for i, m in enumerate(h2_matches):
        start = m.start()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(content)
        section = content[start:end].strip()
        if section:
            sections.append(section)

    return sections


def build_acf_page_content(
    html_content: str,
    large_image_id: int,
    two_col_image_ids: List[int] | None = None,
    template: str | None = None,
) -> dict:
    """
    Build a full ACF block stream for a typical interior landing page.
    Returns payload fields to merge into a WP update/create request.
    """
    sections = split_content_by_h2(html_content)
    blocks: List[str] = []

    if sections:
        blocks.append(html_to_acf_content_block(sections[0]))
    blocks.append(create_large_image_block(large_image_id))

    for idx, section in enumerate(sections[1:], start=1):
        blocks.append(html_to_acf_content_block(section))
        # Insert 2-col images after the first major section (if provided)
        if idx == 1 and two_col_image_ids and len(two_col_image_ids) >= 2:
            blocks.append(create_two_column_images_block(two_col_image_ids[0], two_col_image_ids[1]))
            blocks.append(create_clearfix_block())

    payload = {"content": "\n\n".join(blocks)}
    # Only set template if explicitly requested; otherwise preserve existing template.
    if template:
        payload["template"] = template
    return payload

