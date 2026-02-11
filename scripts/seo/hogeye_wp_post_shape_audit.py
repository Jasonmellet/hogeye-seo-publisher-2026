#!/usr/bin/env python3
"""
Read-only audit of the "average" WordPress post shape.

Purpose:
- Confirm Gutenberg (block) vs raw HTML patterns
- Identify whether AIOSEO meta fields are exposed via REST
- Summarize taxonomy + featured image conventions

This script does NOT create, update, or delete any content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def _extract_block_types(content: str) -> List[str]:
    # Matches Gutenberg serialized blocks: <!-- wp:paragraph -->, <!-- wp:heading {"level":2} -->, etc.
    return re.findall(r"<!--\s*wp:([a-z0-9_-]+/[a-z0-9_-]+|[a-z0-9_-]+)", content or "", flags=re.IGNORECASE)


def _safe_len(x: Any) -> int:
    return len(x) if isinstance(x, str) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only audit of WP post structure.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--count", type=int, default=10, help="How many recent posts to sample (default 10)")
    ap.add_argument("--output", default="work/seo/hogeye/wp_post_shape_audit.json", help="Where to write report JSON")
    args = ap.parse_args()

    load_dotenv(str(Path(args.project_root) / ".env"), override=False)
    wp_site_url = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    wp_username = (os.environ.get("WP_USERNAME") or "").strip()
    wp_app_password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not wp_site_url or not wp_username or not wp_app_password:
        raise SystemExit("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env")

    session = requests.Session()
    session.auth = HTTPBasicAuth(wp_username, wp_app_password)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
    )

    def api_url(path: str) -> str:
        return f"{wp_site_url}/wp-json/wp/v2/{path.lstrip('/')}"

    # Pull recent posts with context=edit so we can see raw content + meta where available.
    resp = session.get(
        api_url("posts"),
        params={
            "per_page": max(1, int(args.count)),
            "orderby": "date",
            "order": "desc",
            "context": "edit",
            "status": "any",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise SystemExit(f"Failed to fetch posts (status={resp.status_code}).")

    posts: List[Dict[str, Any]] = resp.json()

    block_type_counter: Counter[str] = Counter()
    has_blocks = 0
    has_aioseo_meta = 0
    aioseo_keys_counter: Counter[str] = Counter()
    category_counts: List[int] = []
    tag_counts: List[int] = []
    featured_media_present = 0

    samples: List[Dict[str, Any]] = []

    for p in posts:
        pid = p.get("id")
        status = p.get("status")
        slug = p.get("slug")
        title = (p.get("title") or {}).get("rendered") if isinstance(p.get("title"), dict) else p.get("title")

        content_obj = p.get("content") or {}
        raw = content_obj.get("raw") if isinstance(content_obj, dict) else ""
        rendered = content_obj.get("rendered") if isinstance(content_obj, dict) else ""

        # Prefer raw for block detection; fall back to rendered.
        content_for_scan = raw or rendered or ""
        blocks = _extract_block_types(content_for_scan)
        if blocks:
            has_blocks += 1
            block_type_counter.update([b.lower() for b in blocks])

        meta = p.get("meta") if isinstance(p.get("meta"), dict) else {}
        aioseo_keys = [k for k in meta.keys() if "aioseo" in str(k).lower()]
        if aioseo_keys:
            has_aioseo_meta += 1
            aioseo_keys_counter.update([k.lower() for k in aioseo_keys])

        cats = p.get("categories") if isinstance(p.get("categories"), list) else []
        tags = p.get("tags") if isinstance(p.get("tags"), list) else []
        category_counts.append(len(cats))
        tag_counts.append(len(tags))

        featured_media = int(p.get("featured_media") or 0)
        if featured_media:
            featured_media_present += 1

        excerpt_obj = p.get("excerpt") or {}
        excerpt_raw = excerpt_obj.get("raw") if isinstance(excerpt_obj, dict) else ""
        excerpt_rendered = excerpt_obj.get("rendered") if isinstance(excerpt_obj, dict) else ""

        samples.append(
            {
                "id": pid,
                "status": status,
                "slug": slug,
                "title": title,
                "has_gutenberg_blocks": bool(blocks),
                "block_type_count": len(blocks),
                "top_block_types": [b for b, _ in Counter([x.lower() for x in blocks]).most_common(10)],
                "content_len_raw": _safe_len(raw),
                "content_len_rendered": _safe_len(rendered),
                "categories_count": len(cats),
                "tags_count": len(tags),
                "featured_media_id": featured_media or None,
                "excerpt_len_raw": _safe_len(excerpt_raw),
                "excerpt_len_rendered": _safe_len(excerpt_rendered),
                "aioseo_meta_keys_present": aioseo_keys[:20],
            }
        )

    def _avg(nums: List[int]) -> float:
        return (sum(nums) / len(nums)) if nums else 0.0

    report: Dict[str, Any] = {
        "sample_size": len(posts),
        "gutenberg_blocks_share": (has_blocks / len(posts)) if posts else 0,
        "aioseo_meta_exposed_share": (has_aioseo_meta / len(posts)) if posts else 0,
        "featured_image_share": (featured_media_present / len(posts)) if posts else 0,
        "avg_categories_per_post": _avg(category_counts),
        "avg_tags_per_post": _avg(tag_counts),
        "top_block_types_overall": block_type_counter.most_common(25),
        "aioseo_meta_keys_overall": aioseo_keys_counter.most_common(50),
        "samples": samples,
        "notes": [
            "If aioseo_meta_exposed_share is 0, AIOSEO fields may not be exposed via REST meta; we may need a plugin setting or alternative method.",
            "If gutenberg_blocks_share is low, posts may be stored as raw HTML/builder output; content generation should match that.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("OK")
    print("wrote:", str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

