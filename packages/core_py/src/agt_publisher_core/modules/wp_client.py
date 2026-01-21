"""
WordPress API client helpers.

Centralizes:
- Cleaning PHP warnings from JSON responses
- Consistent GET/POST patterns with context=edit
- Lookup helpers (by slug) to avoid duplicate creation
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from agt_publisher_core.config import Config


def clean_json_response(text: str) -> str:
    """
    WordPress sometimes includes PHP warnings/notices before the JSON.
    This strips everything before the first '{' (or '[') for parsing.
    """
    obj_start = text.find("{")
    arr_start = text.find("[")

    if obj_start == -1 and arr_start == -1:
        return text

    if obj_start == -1:
        return text[arr_start:]
    if arr_start == -1:
        return text[obj_start:]

    return text[min(obj_start, arr_start) :]


@dataclass(frozen=True)
class WPResponse:
    ok: bool
    status_code: int
    data: Optional[Any]
    text: str


class WordPressClient:
    def __init__(self, session):
        self.session = session

    def get_json(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> WPResponse:
        resp = self.session.get(Config.get_api_url(endpoint), params=params or {}, timeout=timeout)
        txt = resp.text or ""
        if resp.status_code < 200 or resp.status_code >= 300:
            return WPResponse(ok=False, status_code=resp.status_code, data=None, text=txt)

        cleaned = clean_json_response(txt)
        try:
            return WPResponse(ok=True, status_code=resp.status_code, data=json.loads(cleaned), text=txt)
        except json.JSONDecodeError:
            # Some endpoints might not return JSON cleanly; still return ok with None data.
            return WPResponse(ok=True, status_code=resp.status_code, data=None, text=txt)

    def post_json(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> WPResponse:
        resp = self.session.post(
            Config.get_api_url(endpoint),
            params=params or {},
            json=payload,
            timeout=timeout,
        )
        txt = resp.text or ""
        if resp.status_code < 200 or resp.status_code >= 300:
            return WPResponse(ok=False, status_code=resp.status_code, data=None, text=txt)

        cleaned = clean_json_response(txt)
        try:
            return WPResponse(ok=True, status_code=resp.status_code, data=json.loads(cleaned), text=txt)
        except json.JSONDecodeError:
            return WPResponse(ok=True, status_code=resp.status_code, data=None, text=txt)

    def find_by_slug(self, content_type: str, slug: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Find a post/page by slug.
        content_type: 'posts' or 'pages'
        """
        r = self.get_json(content_type, params={"slug": slug, "status": "any", "per_page": 1})
        if not r.ok or not isinstance(r.data, list):
            return False, None
        if not r.data:
            return False, None
        return True, r.data[0]

