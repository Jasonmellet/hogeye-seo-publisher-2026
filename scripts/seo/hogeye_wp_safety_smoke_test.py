#!/usr/bin/env python3
"""
Hogeye WP safety smoke test (writes + rollback).

This is intentionally minimal and avoids project-level dependencies.

What it does:
1) Auth check (read-only)
2) Create a single DRAFT post
3) Fetch it back (context=edit)
4) Force-delete it (rollback), unless --keep is passed
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def _write_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Create+rollback a WP draft post (smoke test).")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--keep", action="store_true", help="Keep the draft post (do not delete).")
    ap.add_argument("--report", default="work/seo/hogeye/wp_smoke_test_report.json", help="Write report JSON here.")
    args = ap.parse_args()

    load_dotenv(str(Path(args.project_root) / ".env"), override=False)
    wp_site_url = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    wp_username = (os.environ.get("WP_USERNAME") or "").strip()
    wp_app_password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not wp_site_url or not wp_username or not wp_app_password:
        raise SystemExit("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env")

    def api_root() -> str:
        return f"{wp_site_url}/wp-json"

    def api_url(path: str) -> str:
        return f"{wp_site_url}/wp-json/wp/v2/{path.lstrip('/')}"

    session = requests.Session()
    session.auth = HTTPBasicAuth(wp_username, wp_app_password)
    # Browser-like headers help avoid security plugin blocks.
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    title = f"SMOKE TEST — DELETE ME — {now}"

    report: Dict[str, Any] = {
        "ran_at": now,
        "wp_site_url": wp_site_url,
        "username": wp_username,
        "created_post": None,
        "fetched_post": None,
        "deleted": None,
        "deleted_status_code": None,
        "notes": [],
    }

    print("WP Safety Smoke Test")
    print("- Create a draft post, then rollback (delete)")
    print(f"- Target: {wp_site_url}")
    print()

    # Read-only auth check
    r_api = session.get(api_root(), timeout=15)
    if r_api.status_code != 200:
        report["notes"].append(f"REST root failed: status={r_api.status_code}")
        _write_report(Path(args.report), report)
        raise SystemExit(f"REST root failed (status={r_api.status_code}).")

    r_me = session.get(api_url("users/me"), timeout=15)
    if r_me.status_code != 200:
        report["notes"].append(f"Auth users/me failed: status={r_me.status_code}, body_prefix={(r_me.text or '')[:200]}")
        _write_report(Path(args.report), report)
        raise SystemExit(f"Auth failed for users/me (status={r_me.status_code}).")

    print("✓ Auth OK")

    create_payload: Dict[str, Any] = {
        "title": title,
        "status": "draft",
        "content": (
            "<!-- wp:paragraph -->"
            "<p>This is an automated smoke-test draft created to verify WordPress REST access. "
            "It should be deleted immediately after verification.</p>"
            "<!-- /wp:paragraph -->"
        ),
    }

    print("Creating draft post...")
    resp_create = session.post(api_url("posts"), params={"context": "edit"}, json=create_payload, timeout=30)
    if resp_create.status_code not in (200, 201):
        report["notes"].append(
            f"Create failed: status={resp_create.status_code}, body_prefix={(resp_create.text or '')[:200]}"
        )
        _write_report(Path(args.report), report)
        raise SystemExit(f"Create failed (status={resp_create.status_code}).")

    created = resp_create.json()
    post_id = int(created.get("id") or 0)
    report["created_post"] = {"id": post_id, "status": created.get("status"), "link": created.get("link")}
    print(f"✓ Draft created (id={post_id})")

    print("Fetching draft post back (context=edit)...")
    resp_get = session.get(api_url(f"posts/{post_id}"), params={"context": "edit"}, timeout=30)
    if resp_get.status_code != 200:
        report["notes"].append(
            f"Fetch failed: status={resp_get.status_code}, body_prefix={(resp_get.text or '')[:200]}"
        )
        _write_report(Path(args.report), report)
        raise SystemExit(f"Fetch failed (status={resp_get.status_code}).")

    fetched = resp_get.json()
    report["fetched_post"] = {
        "id": int(fetched.get("id") or 0),
        "status": fetched.get("status"),
        "slug": fetched.get("slug"),
        "title": (fetched.get("title") or {}).get("rendered") if isinstance(fetched.get("title"), dict) else fetched.get("title"),
        "has_meta": isinstance(fetched.get("meta"), dict),
    }
    print("✓ Draft fetched")

    if args.keep:
        report["deleted"] = False
        report["notes"].append("Kept draft post due to --keep.")
        _write_report(Path(args.report), report)
        print("Keeping draft post due to --keep.")
        print(f"Draft post id={post_id}")
        return 0

    print("Rolling back (force delete)...")
    resp_del = session.delete(api_url(f"posts/{post_id}"), params={"force": True}, timeout=30)
    report["deleted_status_code"] = resp_del.status_code
    report["deleted"] = resp_del.status_code in (200, 410)
    if resp_del.status_code not in (200, 410):
        report["notes"].append(
            f"Delete failed: status={resp_del.status_code}, body_prefix={(resp_del.text or '')[:200]}"
        )
        _write_report(Path(args.report), report)
        raise SystemExit(f"Delete failed (status={resp_del.status_code}).")

    print("✓ Deleted")
    _write_report(Path(args.report), report)
    print(f"Report written to {args.report}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

