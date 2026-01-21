"""
Post-update verification gates.

Goal: after we publish/update a page/post, we immediately refetch and validate
the content meets our "90% correct on first publish" bar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: List[str]
    warnings: List[str]


def _extract_image_ids(content: str) -> List[int]:
    return [int(x) for x in re.findall(r"wp-image-(\d+)", content)]


def validate_blog_post(
    *,
    content: str,
    featured_media_id: int,
    min_content_images: int = 2,
    max_content_images: int = 4,
    require_featured_not_in_body: bool = True,
    required_faq_questions: Optional[int] = 5,
) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    image_ids = _extract_image_ids(content)
    unique_ids: Set[int] = set(image_ids)

    # Featured image should not appear in body
    if require_featured_not_in_body and featured_media_id and featured_media_id in unique_ids:
        errors.append(f"Featured image (ID {featured_media_id}) appears in post body.")

    # Image count bounds
    content_image_count = len(unique_ids) - (1 if featured_media_id in unique_ids else 0)
    if content_image_count < min_content_images:
        errors.append(f"Too few content images ({content_image_count}). Expected >= {min_content_images}.")
    if content_image_count > max_content_images:
        warnings.append(f"Many content images ({content_image_count}). Consider reducing to {max_content_images}.")

    # Duplicate image IDs (exact repeats)
    dupes = sorted({img for img in unique_ids if image_ids.count(img) > 1})
    if dupes:
        warnings.append(f"Duplicate image IDs appear multiple times in body: {dupes}")

    # FAQ count (visible)
    if required_faq_questions is not None:
        faq_match = re.search(
            r"<h2[^>]*>\s*Frequently Asked Questions\s*</h2>(.*?)(?=<h2|$)",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not faq_match:
            errors.append("FAQ section not found (missing H2 'Frequently Asked Questions').")
        else:
            faq_section = faq_match.group(1)
            questions = re.findall(r"<h3[^>]*>.*?</h3>", faq_section, flags=re.IGNORECASE | re.DOTALL)
            if len(questions) != required_faq_questions:
                errors.append(f"FAQ question count is {len(questions)}; expected {required_faq_questions}.")

    # Link placeholders
    if "{{link:" in content:
        warnings.append("Unresolved internal link placeholders remain ({{link:...}}).")

    # TOC duplicates
    toc_divs = len(re.findall(r"table-of-contents", content, flags=re.IGNORECASE))
    if toc_divs > 3:  # heuristic: toc div + styles + class refs; high count suggests duplicates
        warnings.append("TOC markers appear many times; verify no duplicated TOCs.")

    return ValidationResult(ok=len(errors) == 0, errors=errors, warnings=warnings)


def validate_landing_page(
    *,
    content: str,
    require_h2: bool = True,
    min_h2: int = 2,
    internal_link_host: str = "",
) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    # Raw ACF block streams store HTML inside JSON-escaped "content" fields.
    # Decode those first so we can correctly count headings.
    decoded_sections: List[str] = []
    for m in re.finditer(r'"content":"(.*?)","_content"', content, flags=re.DOTALL):
        try:
            decoded = __import__("json").loads('"' + m.group(1) + '"')
            if decoded:
                decoded_sections.append(decoded)
        except Exception:
            continue

    if decoded_sections:
        h2_count = sum(len(re.findall(r"<h2[^>]*>", s, flags=re.IGNORECASE)) for s in decoded_sections)
    else:
        h2_count = len(re.findall(r"<h2[^>]*>", content, flags=re.IGNORECASE))
    if require_h2 and h2_count < min_h2:
        errors.append(f"Too few H2 headings ({h2_count}); expected >= {min_h2}.")

    if "{{link:" in content:
        warnings.append("Unresolved internal link placeholders remain ({{link:...}}).")

    # Internal links (decode ACF JSON-escaped HTML when present)
    if decoded_sections:
        joined = "\n".join(decoded_sections)
        if internal_link_host:
            internal_links = len(re.findall(rf'href="https?://{re.escape(internal_link_host)}/', joined, flags=re.IGNORECASE))
        else:
            internal_links = 0
    else:
        # In raw ACF streams, quotes and tags may be JSON-escaped (e.g., \u003c, \u0022)
        if internal_link_host:
            internal_links = len(
                re.findall(rf'href=(?:\\u0022|\\"|")https?://{re.escape(internal_link_host)}/', content, flags=re.IGNORECASE)
            )
        else:
            internal_links = 0

    if internal_links == 0:
        warnings.append("No internal links detected on landing page (0 internal hrefs).")

    return ValidationResult(ok=len(errors) == 0, errors=errors, warnings=warnings)

