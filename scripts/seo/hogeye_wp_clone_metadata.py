#!/usr/bin/env python3
"""
Hogeye WP metadata "clone" (read-only export).

Exports *metadata + copy* for all posts + pages so we have a local "source of truth"
to:
- avoid duplicate/cannibalizing content (slug/title/SEO meta comparisons)
- fact-check new drafts against what is already published
- track changes over time (re-run exporter and diff snapshots)

Notes:
- This script does NOT write to WordPress.
- It exports copy as **plain text** by default (HTML stripped).
- It will export AIOSEO fields if exposed via REST (aioseo_meta_data, meta[aioseo_*]).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rendered_text(x: Any) -> str:
    if isinstance(x, dict):
        v = x.get("rendered")
        return v if isinstance(v, str) else ""
    return x if isinstance(x, str) else ""


def _safe_int(x: Any) -> int:
    try:
        return int(x)
    except Exception:
        return 0


class _HTMLTextExtractor(HTMLParser):
    """
    Minimal HTML -> text extractor (stdlib only).
    - Drops tags
    - Adds whitespace around block-ish tags so text doesn't smash together
    """

    _BLOCK_TAGS = {
        "p",
        "br",
        "div",
        "li",
        "ul",
        "ol",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "pre",
        "code",
        "table",
        "tr",
        "td",
        "th",
        "hr",
    }

    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self._parts.append(data)

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            self._parts.append("\n")

    def text(self) -> str:
        return "".join(self._parts)


_WP_BLOCK_COMMENTS_RE = re.compile(r"<!--\s*/?\s*wp:[^>]*-->", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def _html_to_text(html: str) -> str:
    """
    Convert WP HTML-ish content to normalized plain text.
    """
    if not html:
        return ""
    # Remove Gutenberg block comments (they're noise for "copy" comparison).
    s = _WP_BLOCK_COMMENTS_RE.sub("", html)
    # Decode entities early (so extractor sees actual punctuation).
    s = unescape(s)
    parser = _HTMLTextExtractor()
    parser.feed(s)
    parser.close()
    out = parser.text()
    # Normalize whitespace: keep newlines, collapse spaces/tabs, collapse excessive blank lines.
    out = out.replace("\u00a0", " ")
    out = _WHITESPACE_RE.sub(" ", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    out = re.sub(r"\n[ \t]+", "\n", out)
    out = _MULTI_NL_RE.sub("\n\n", out)
    return out.strip()


def _sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _api_url(wp_site_url: str, path: str) -> str:
    return f"{wp_site_url}/wp-json/wp/v2/{path.lstrip('/')}"


def _request_with_retries(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    max_retries: int = 5,
) -> requests.Response:
    last_exc: Optional[BaseException] = None
    for attempt in range(max_retries):
        try:
            resp = session.request(method, url, params=params or {}, timeout=timeout)
            # Retry transient server errors + rate limiting.
            if resp.status_code in (429, 500, 502, 503, 504):
                sleep_s = min(10.0, 0.75 * (2**attempt))
                time.sleep(sleep_s)
                continue
            return resp
        except requests.RequestException as e:
            last_exc = e
            sleep_s = min(10.0, 0.75 * (2**attempt))
            time.sleep(sleep_s)
    raise SystemExit(f"Request failed after retries: {method} {url} ({last_exc})")


def _iter_wp_list(
    session: requests.Session,
    wp_site_url: str,
    endpoint: str,
    *,
    base_params: Dict[str, Any],
    per_page: int,
    timeout: int,
) -> Iterable[Tuple[int, List[Dict[str, Any]], Dict[str, str]]]:
    """
    Yields (page_number, items, headers) for each page.
    """
    page = 1
    while True:
        params = dict(base_params)
        params["per_page"] = per_page
        params["page"] = page

        url = _api_url(wp_site_url, endpoint)
        resp = _request_with_retries(session, "GET", url, params=params, timeout=timeout)

        # WordPress uses 400 for out-of-range pages sometimes.
        if resp.status_code == 400:
            break
        if resp.status_code != 200:
            raise SystemExit(
                f"Failed to fetch {endpoint} page={page} (status={resp.status_code}). body_prefix={(resp.text or '')[:200]}"
            )

        data = resp.json()
        if not isinstance(data, list):
            raise SystemExit(f"Unexpected response shape for {endpoint} page={page} (expected list).")

        yield page, data, dict(resp.headers)

        total_pages = _safe_int(resp.headers.get("X-WP-TotalPages"))
        if total_pages and page >= total_pages:
            break
        if len(data) < per_page:
            break
        page += 1


def _extract_aioseo_from_item(item: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    if isinstance(item.get("aioseo_meta_data"), dict):
        out["aioseo_meta_data"] = item["aioseo_meta_data"]

    meta = item.get("meta")
    if isinstance(meta, dict):
        aioseo_meta = {k: v for k, v in meta.items() if "aioseo" in str(k).lower()}
        if aioseo_meta:
            out["wp_meta_aioseo"] = aioseo_meta

    # Presence flags are handy for debugging without exporting giant payloads.
    out["aioseo_fields_present"] = {
        "aioseo_meta_data": "aioseo_meta_data" in item,
        "aioseo_head_json": "aioseo_head_json" in item,
        "aioseo_head": "aioseo_head" in item,
    }
    return out


def _normalize_post_or_page(
    item: Dict[str, Any],
    kind: str,
    *,
    include_copy: bool,
    copy_source: str,
    include_copy_hashes: bool,
) -> Dict[str, Any]:
    # kind: "posts" or "pages"
    normalized: Dict[str, Any] = {
        "id": _safe_int(item.get("id")),
        "kind": "post" if kind == "posts" else "page",
        "status": item.get("status"),
        "link": item.get("link"),
        "slug": item.get("slug"),
        "title": _rendered_text(item.get("title")),
        "date_gmt": item.get("date_gmt") or item.get("date"),
        "modified_gmt": item.get("modified_gmt") or item.get("modified"),
        "author": _safe_int(item.get("author")),
        "featured_media": _safe_int(item.get("featured_media")),
    }

    if kind == "posts":
        normalized.update(
            {
                "categories": item.get("categories") if isinstance(item.get("categories"), list) else [],
                "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
                "sticky": bool(item.get("sticky")) if "sticky" in item else None,
                "format": item.get("format"),
            }
        )
    else:
        normalized.update(
            {
                "parent": _safe_int(item.get("parent")),
                "menu_order": _safe_int(item.get("menu_order")),
                "template": item.get("template"),
            }
        )

    if include_copy:
        content_obj = item.get("content") if isinstance(item.get("content"), dict) else {}
        excerpt_obj = item.get("excerpt") if isinstance(item.get("excerpt"), dict) else {}

        def pick(obj: Dict[str, Any]) -> str:
            if copy_source == "raw":
                v = obj.get("raw")
                return v if isinstance(v, str) else ""
            # rendered (default) tends to exist even when raw is absent
            v = obj.get("rendered")
            return v if isinstance(v, str) else ""

        content_src = pick(content_obj)
        excerpt_src = pick(excerpt_obj)
        content_text = _html_to_text(content_src)
        excerpt_text = _html_to_text(excerpt_src)

        normalized.update(
            {
                "copy": {
                    "content_text": content_text,
                    "excerpt_text": excerpt_text,
                    "content_source": copy_source,
                }
            }
        )
        if include_copy_hashes:
            normalized["copy_hashes"] = {
                "content_sha256": _sha256_text(content_text),
                "excerpt_sha256": _sha256_text(excerpt_text),
            }

    normalized.update(_extract_aioseo_from_item(item))
    return normalized


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")
            n += 1
    return n


def _export_taxonomy(
    session: requests.Session,
    wp_site_url: str,
    taxonomy_endpoint: str,
    *,
    per_page: int,
    timeout: int,
) -> Dict[str, Any]:
    by_id: Dict[str, Any] = {}
    total = 0

    for _, items, _headers in _iter_wp_list(
        session,
        wp_site_url,
        taxonomy_endpoint,
        base_params={"context": "edit", "orderby": "id", "order": "asc", "hide_empty": False},
        per_page=per_page,
        timeout=timeout,
    ):
        for t in items:
            tid = _safe_int(t.get("id"))
            if not tid:
                continue
            by_id[str(tid)] = {
                "id": tid,
                "name": t.get("name"),
                "slug": t.get("slug"),
                "link": t.get("link"),
                "parent": _safe_int(t.get("parent")),
                "count": _safe_int(t.get("count")),
            }
            total += 1

    return {"endpoint": taxonomy_endpoint, "total": total, "by_id": by_id}


def main() -> int:
    ap = argparse.ArgumentParser(description="Export WordPress posts/pages metadata (read-only).")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument(
        "--output-dir",
        default="work/seo/hogeye/source_of_truth/wp",
        help="Output directory for source-of-truth snapshot files.",
    )
    ap.add_argument("--status", default="any", help="WP status filter (default: any).")
    ap.add_argument("--per-page", type=int, default=100, help="WP REST per_page (max 100).")
    ap.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    ap.add_argument("--skip-taxonomies", action="store_true", help="Skip exporting categories/tags.")
    ap.add_argument(
        "--include-copy",
        action="store_true",
        help="Include all post/page copy (as plain text; HTML stripped).",
    )
    ap.add_argument(
        "--copy-source",
        choices=["rendered", "raw"],
        default="rendered",
        help="Which WP field to use as the copy source before stripping HTML (default: rendered).",
    )
    ap.add_argument(
        "--include-copy-hashes",
        action="store_true",
        help="Include SHA-256 hashes of normalized copy for fast duplicate detection.",
    )
    args = ap.parse_args()

    per_page = max(1, min(100, int(args.per_page)))

    load_dotenv(str(Path(args.project_root) / ".env"), override=False)
    wp_site_url = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    wp_username = (os.environ.get("WP_USERNAME") or "").strip()
    wp_app_password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not wp_site_url or not wp_username or not wp_app_password:
        raise SystemExit("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.auth = HTTPBasicAuth(wp_username, wp_app_password)
    # Browser-like headers help avoid security plugin blocks.
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
    )

    ran_at = _utc_now()

    # Auth check (read-only)
    r_me = _request_with_retries(session, "GET", _api_url(wp_site_url, "users/me"), timeout=args.timeout)
    if r_me.status_code != 200:
        raise SystemExit(f"Auth failed for users/me (status={r_me.status_code}). body_prefix={(r_me.text or '')[:200]}")

    manifest: Dict[str, Any] = {
        "ran_at": ran_at,
        "wp_site_url": wp_site_url,
        "username": wp_username,
        "filters": {"status": args.status, "per_page": per_page},
        "outputs": {},
        "counts": {},
        "notes": [
            "These exports include metadata and (optionally) copy as plain text (HTML stripped).",
            "Re-run this exporter after publishing/updating content to refresh the local source of truth.",
        ],
    }

    def export_kind(kind: str) -> int:
        base_params = {
            "per_page": per_page,
            "orderby": "id",
            "order": "asc",
            "context": "edit",
            "status": args.status,
        }

        def rows() -> Iterable[Dict[str, Any]]:
            for _page, items, _headers in _iter_wp_list(
                session,
                wp_site_url,
                kind,
                base_params=base_params,
                per_page=per_page,
                timeout=args.timeout,
            ):
                for item in items:
                    yield _normalize_post_or_page(
                        item,
                        kind,
                        include_copy=bool(args.include_copy),
                        copy_source=str(args.copy_source),
                        include_copy_hashes=bool(args.include_copy_hashes),
                    )

        filename = f"{kind}_metadata.jsonl"
        path = out_dir / filename
        n = _write_jsonl(path, rows())
        manifest["outputs"][kind] = str(path)
        manifest["counts"][kind] = n
        return n

    posts_n = export_kind("posts")
    pages_n = export_kind("pages")

    if not args.skip_taxonomies:
        tax = {
            "categories": _export_taxonomy(session, wp_site_url, "categories", per_page=per_page, timeout=args.timeout),
            "tags": _export_taxonomy(session, wp_site_url, "tags", per_page=per_page, timeout=args.timeout),
        }
        tax_path = out_dir / "taxonomies.json"
        _write_json(tax_path, tax)
        manifest["outputs"]["taxonomies"] = str(tax_path)

    manifest["counts"]["total"] = int(posts_n) + int(pages_n)
    manifest_path = out_dir / "snapshot_manifest.json"
    _write_json(manifest_path, manifest)

    print("OK")
    print("wrote:", str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

