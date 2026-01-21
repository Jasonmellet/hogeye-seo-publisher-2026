"""
Robust source loader for content JSON files.

Why this exists:
- Some source JSON files contain large HTML strings that occasionally break strict json.loads
  due to unescaped characters or editor-induced changes.
- We need a single, shared loader that all scripts use, to avoid drift and missing-tail bugs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class LoadedContent:
    source_path: str
    data: Dict[str, Any]
    used_fallback: bool


def _unescape_content_string(s: str) -> str:
    # Common JSON escapes inside HTML strings
    return s.replace("\\n", "\n").replace('\\"', '"').replace("\\/", "/").replace("&amp;", "&")


def _extract_json_string_field(raw: str, field_name: str) -> Optional[str]:
    """
    Extract a JSON string field value from raw JSON text without fully parsing the JSON.

    This is purposely conservative and only supports string fields like "content": "....".
    """
    needle = f'"{field_name}":'
    start = raw.find(needle)
    if start == -1:
        return None

    # Find first quote after colon
    i = start + len(needle)
    while i < len(raw) and raw[i] in [" ", "\t", "\n", "\r"]:
        i += 1
    if i >= len(raw) or raw[i] != '"':
        return None
    i += 1  # move past opening quote

    # Scan until unescaped closing quote that is followed by , or }
    out_chars = []
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and i + 1 < len(raw):
            # Keep escape + escaped char; we'll unescape later with _unescape_content_string
            out_chars.append(ch)
            out_chars.append(raw[i + 1])
            i += 2
            continue

        if ch == '"':
            # lookahead to see if this is the end of the field value
            j = i + 1
            while j < len(raw) and raw[j] in [" ", "\t", "\n", "\r"]:
                j += 1
            if j < len(raw) and raw[j] in [",", "}"]:
                break
            # Otherwise it's a quote inside some other JSON fragment; treat as content
            out_chars.append(ch)
            i += 1
            continue

        out_chars.append(ch)
        i += 1

    return "".join(out_chars)


def _extract_json_int_field(raw: str, field_name: str) -> Optional[int]:
    """
    Extract an integer field like: "acf_large_image_id": 1773
    """
    import re

    m = re.search(rf'"{re.escape(field_name)}"\s*:\s*(\d+)', raw)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _extract_json_int_array_field(raw: str, field_name: str) -> Optional[list[int]]:
    """
    Extract an int array field like: "acf_two_col_image_ids": [1784, 1643]
    """
    import re

    m = re.search(rf'"{re.escape(field_name)}"\s*:\s*\[([^\]]*)\]', raw)
    if not m:
        return None
    nums = re.findall(r"\d+", m.group(1))
    out: list[int] = []
    for n in nums:
        try:
            out.append(int(n))
        except Exception:
            continue
    return out or None


def load_content_file(source_path: str) -> LoadedContent:
    """
    Load a content JSON file. Falls back to manual extraction of core fields if JSON parsing fails.

    Returns:
        LoadedContent with .data containing at minimum the keys it can recover.
    """
    path = Path(source_path)
    raw = path.read_text(encoding="utf-8")

    try:
        data = json.loads(raw)
        # Normalize common JSON-escaped sequences inside HTML strings.
        # Some source files include HTML attributes with backslash-escaped quotes (e.g. href=\"...\"),
        # which should be turned into valid HTML quotes (href="...") before publishing.
        for key in ["title", "slug", "excerpt", "meta_title", "meta_description", "date", "content"]:
            if isinstance(data.get(key), str):
                data[key] = _unescape_content_string(data[key])
        return LoadedContent(source_path=source_path, data=data, used_fallback=False)
    except json.JSONDecodeError:
        # Fallback: recover known fields
        recovered: Dict[str, Any] = {}

        for key in ["title", "slug", "excerpt", "meta_title", "meta_description", "date"]:
            val = _extract_json_string_field(raw, key)
            if val is not None:
                recovered[key] = _unescape_content_string(val)

        content_val = _extract_json_string_field(raw, "content")
        if content_val is not None:
            recovered["content"] = _unescape_content_string(content_val)

        # Common numeric/config fields used by the canonical pipeline
        for key in ["acf_large_image_id", "featured_media_id", "content_image_count"]:
            v = _extract_json_int_field(raw, key)
            if v is not None:
                recovered[key] = v

        for key in ["acf_two_col_image_ids"]:
            arr = _extract_json_int_array_field(raw, key)
            if arr is not None:
                recovered[key] = arr

        # Also support legacy "status" and flags like _update_existing if they are present as literals
        if '"_update_existing"' in raw:
            # simple boolean-ish detection
            recovered["_update_existing"] = '"_update_existing": true' in raw.lower()

        return LoadedContent(source_path=source_path, data=recovered, used_fallback=True)

