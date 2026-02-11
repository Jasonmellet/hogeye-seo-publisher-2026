#!/usr/bin/env python3
"""
Publish a WordPress *draft post* from a local JSON file and set AIOSEO meta via REST.

Why this script exists:
- Hogeye wants images handled manually (Casey), but the canonical pipeline auto-selects media.
- We still want automated, deterministic draft creation + AIOSEO title/description.

Input JSON shape (minimal):
{
  "title": "...",
  "slug": "...",
  "content": "<p>...</p>",
  "excerpt": "...",
  "meta_title": "...",
  "meta_description": "...",
  "status": "draft",
  "categories": ["Camera Resources"],
  "tags": ["hog trap camera", "remote trap closure"]
}
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def _load_item(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Content JSON must be an object.")
    for k in ["title", "content", "meta_title", "meta_description"]:
        if not (data.get(k) or "").strip():
            raise ValueError(f"Missing required field: {k}")
    data.setdefault("status", "draft")
    return data


def _write_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _parse_name_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        v = value.strip()
        return [v] if v else []
    if isinstance(value, list):
        out: List[str] = []
        for x in value:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
        return out
    return []


def _wp_session(project_root: Path) -> tuple[requests.Session, str]:
    load_dotenv(str(project_root / ".env"), override=False)
    wp_site_url = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    wp_username = (os.environ.get("WP_USERNAME") or "").strip()
    wp_app_password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not wp_site_url or not wp_username or not wp_app_password:
        raise SystemExit("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env")

    session = requests.Session()
    session.auth = HTTPBasicAuth(wp_username, wp_app_password)
    session.headers.update(
        {
            # Some sites/WAFs block generic python clients; use a browser-like UA.
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
    )
    return session, wp_site_url


def _api_url(site_url: str, path: str) -> str:
    return f"{site_url}/wp-json/wp/v2/{path.lstrip('/')}"


def _post_json(session: requests.Session, url: str, payload: Dict[str, Any], *, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    return session.post(url, params=params or {}, json=payload, timeout=60)

def _get_or_create_term_id(session: requests.Session, site_url: str, endpoint: str, name: str) -> int:
    """
    Create term by name (categories/tags) and return its ID.
    - If it already exists, WordPress returns 400 term_exists with data.term_id.
    """
    nm = (name or "").strip()
    if not nm:
        return 0
    url = _api_url(site_url, endpoint)
    r = _post_json(session, url, {"name": nm}, params={"context": "edit"})
    if r.status_code in (200, 201):
        try:
            return int((r.json() or {}).get("id") or 0)
        except Exception:
            return 0
    if r.status_code == 400:
        try:
            j = r.json()
        except Exception:
            return 0
        if j.get("code") == "term_exists" and isinstance(j.get("data"), dict) and j["data"].get("term_id"):
            try:
                return int(j["data"]["term_id"])
            except Exception:
                return 0
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish draft post + set AIOSEO meta.")
    ap.add_argument("content_json", help="Absolute/relative path to content JSON")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument(
        "--report",
        default="work/seo/hogeye/draft_publish_report.json",
        help="Write report JSON here.",
    )
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    item_path = Path(args.content_json).resolve()
    item = _load_item(item_path)

    session, site_url = _wp_session(project_root)

    ran_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    report: Dict[str, Any] = {
        "ran_at": ran_at,
        "site_url": site_url,
        "source_file": str(item_path),
        "created_post_id": None,
        "created_post_link": None,
        "aioseo_update_status_code": None,
        "fetched_has_aioseo_meta_data": None,
        "created_category_ids": [],
        "created_tag_ids": [],
        "notes": [],
    }

    # Create draft post (always create; we cannot rely on listing endpoints for slug lookups on this site)
    category_names = _parse_name_list(item.get("categories"))
    tag_names = _parse_name_list(item.get("tags"))

    cat_ids: List[int] = []
    for name in category_names:
        cid = _get_or_create_term_id(session, site_url, "categories", name)
        if cid:
            cat_ids.append(cid)
    tag_ids: List[int] = []
    for name in tag_names:
        tid = _get_or_create_term_id(session, site_url, "tags", name)
        if tid:
            tag_ids.append(tid)

    report["created_category_ids"] = cat_ids
    report["created_tag_ids"] = tag_ids

    payload: Dict[str, Any] = {
        "title": item["title"],
        "slug": item.get("slug") or "",
        "status": item.get("status") or "draft",
        "content": item["content"],
        "excerpt": item.get("excerpt") or "",
    }
    if cat_ids:
        payload["categories"] = cat_ids
    if tag_ids:
        payload["tags"] = tag_ids

    resp_create = _post_json(session, _api_url(site_url, "posts"), payload, params={"context": "edit"})
    if resp_create.status_code not in (200, 201):
        report["notes"].append(f"Create failed: status={resp_create.status_code}, body_prefix={(resp_create.text or '')[:400]}")
        _write_report(Path(args.report), report)
        raise SystemExit(f"Create failed (status={resp_create.status_code}).")

    created = resp_create.json()
    post_id = int(created.get("id") or 0)
    report["created_post_id"] = post_id
    report["created_post_link"] = created.get("link")

    # Set AIOSEO meta title/description
    aioseo_payload = {
        "aioseo_meta_data": {
            "title": item.get("meta_title") or "",
            "description": item.get("meta_description") or "",
        }
    }
    resp_aio = _post_json(session, _api_url(site_url, f"posts/{post_id}"), aioseo_payload, params={"context": "edit"})
    report["aioseo_update_status_code"] = resp_aio.status_code
    if resp_aio.status_code not in (200, 201):
        report["notes"].append(
            f"AIOSEO update failed: status={resp_aio.status_code}, body_prefix={(resp_aio.text or '')[:400]}"
        )

    # Fetch back to confirm AIOSEO fields present
    resp_get = session.get(_api_url(site_url, f"posts/{post_id}"), params={"context": "edit"}, timeout=60)
    if resp_get.status_code != 200:
        report["notes"].append(f"Fetch failed: status={resp_get.status_code}, body_prefix={(resp_get.text or '')[:400]}")
        _write_report(Path(args.report), report)
        raise SystemExit(f"Fetch failed (status={resp_get.status_code}).")

    fetched = resp_get.json()
    report["fetched_has_aioseo_meta_data"] = isinstance(fetched.get("aioseo_meta_data"), dict)

    _write_report(Path(args.report), report)

    print("Draft created")
    print(f"- Post ID: {post_id}")
    print(f"- URL: {report['created_post_link']}")
    print(f"- AIOSEO meta update status: {report['aioseo_update_status_code']}")
    print(f"- Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

