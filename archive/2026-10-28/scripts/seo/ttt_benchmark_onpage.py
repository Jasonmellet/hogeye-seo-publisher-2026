#!/usr/bin/env python3
"""
Run a DataForSEO OnPage crawl benchmark and export CSVs.

Outputs (in --output-dir):
  - Benchmark_OnPage_Summary.csv
  - Benchmark_OnPage_IssueCounts.csv
  - Benchmark_OnPage_Pages.csv
  - Benchmark_OnPage_NonIndexable.csv

Notes:
  - Only the task POST is billable; subsequent GET/POST reads are free for 30 days.
  - Defaults are intentionally conservative to control crawl size/cost.
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

API_BASE = "https://api.dataforseo.com/v3"


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _infer_target_domain() -> str:
    wp_site = (os.environ.get("WP_SITE_URL") or "").strip()
    host = (urlparse(wp_site).hostname or "").strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _dfs_post(login: str, password: str, path: str, payload: list[dict], timeout: int = 120) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.post(url, json=payload, auth=(login, password), timeout=timeout)
    r.raise_for_status()
    return r.json()


def _dfs_get(login: str, password: str, path: str, timeout: int = 120) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.get(url, auth=(login, password), timeout=timeout)
    r.raise_for_status()
    return r.json()


def onpage_task_post(
    *,
    login: str,
    password: str,
    target: str,
    max_crawl_pages: int,
    crawl_delay_ms: int,
    respect_sitemap: bool,
    crawl_sitemap_only: bool,
    tag: str,
) -> str:
    payload = [
        {
            "target": target,
            "max_crawl_pages": max_crawl_pages,
            "crawl_delay": crawl_delay_ms,
            "respect_sitemap": respect_sitemap,
            "crawl_sitemap_only": crawl_sitemap_only,
            "tag": tag,
        }
    ]
    data = _dfs_post(login, password, "/on_page/task_post", payload, timeout=60)
    tasks = data.get("tasks") or []
    if not tasks:
        raise RuntimeError("OnPage task_post returned no tasks.")
    t0 = tasks[0]
    status_code = int(t0.get("status_code") or 0)
    if status_code >= 40000:
        raise RuntimeError(f"OnPage task_post failed: {t0.get('status_code')} {t0.get('status_message')}")
    task_id = t0.get("id")
    if not task_id:
        raise RuntimeError("OnPage task_post missing task id.")
    return str(task_id)


def onpage_summary(*, login: str, password: str, task_id: str) -> dict:
    data = _dfs_get(login, password, f"/on_page/summary/{task_id}", timeout=60)
    tasks = data.get("tasks") or []
    if not tasks:
        return {"_status_code": "", "_status_message": "No tasks in response."}
    t0 = tasks[0]
    status_code = t0.get("status_code")
    status_message = t0.get("status_message")
    res = t0.get("result") or []
    if not res:
        return {"_status_code": status_code, "_status_message": status_message}
    obj = res[0] if isinstance(res[0], dict) else {}
    obj["_status_code"] = status_code
    obj["_status_message"] = status_message
    return obj


def onpage_pages(
    *,
    login: str,
    password: str,
    task_id: str,
    limit: int,
    offset: int,
) -> dict:
    payload = [
        {
            "id": task_id,
            "filters": [["resource_type", "=", "html"]],
            "limit": limit,
            "offset": offset,
            "order_by": ["click_depth,asc"],
        }
    ]
    data = _dfs_post(login, password, "/on_page/pages", payload, timeout=120)
    tasks = data.get("tasks") or []
    res = (tasks[0].get("result") or []) if tasks else []
    return res[0] if res else {}


def onpage_non_indexable(
    *,
    login: str,
    password: str,
    task_id: str,
    limit: int,
    offset: int,
) -> dict:
    payload = [{"id": task_id, "limit": limit, "offset": offset}]
    data = _dfs_post(login, password, "/on_page/non_indexable", payload, timeout=120)
    tasks = data.get("tasks") or []
    res = (tasks[0].get("result") or []) if tasks else []
    return res[0] if res else {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run DataForSEO OnPage benchmark and export CSVs.")
    ap.add_argument("--project-root", default=str(Path.cwd()), help="Project root (to load .env)")
    ap.add_argument("--output-dir", required=True, help="Benchmark output directory")
    ap.add_argument("--target", default="", help="Target domain (no https/www). Defaults to WP_SITE_URL host.")
    ap.add_argument("--task-id", default="", help="Reuse an existing OnPage task id (skips creating a new crawl)")
    ap.add_argument("--max-crawl-pages", type=int, default=500, help="OnPage crawl cap (default 500)")
    ap.add_argument("--crawl-delay-ms", type=int, default=2000, help="Delay between hits in ms (default 2000)")
    ap.add_argument("--respect-sitemap", action="store_true", help="Respect primary sitemap ordering")
    ap.add_argument("--crawl-sitemap-only", action="store_true", help="Only crawl pages listed in sitemap")
    ap.add_argument("--poll-seconds", type=int, default=10, help="Seconds between summary polls")
    ap.add_argument("--max-wait-seconds", type=int, default=1800, help="Max wait for crawl completion (default 30 min)")
    ap.add_argument("--export-pages", type=int, default=500, help="Max pages to export to CSV (default 500)")
    ap.add_argument("--export-nonindexable", type=int, default=2000, help="Max non-indexable rows to export (default 2000)")
    ap.add_argument("--tag", default="ttt_onpage_benchmark", help="DataForSEO task tag")
    args = ap.parse_args()

    load_dotenv(os.path.join(args.project_root, ".env"), override=False)
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        raise SystemExit("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in .env.")

    target = (args.target or _infer_target_domain()).strip().lower()
    if target.startswith("www."):
        target = target[4:]
    if not target:
        raise SystemExit("Missing --target and could not infer from WP_SITE_URL.")

    fetched_at = datetime.now(timezone.utc).isoformat()

    task_id = (args.task_id or "").strip()
    if task_id:
        print(f"Reusing OnPage task: {task_id}", flush=True)
    else:
        task_id = onpage_task_post(
            login=login,
            password=password,
            target=target,
            max_crawl_pages=max(1, int(args.max_crawl_pages)),
            crawl_delay_ms=max(0, int(args.crawl_delay_ms)),
            respect_sitemap=bool(args.respect_sitemap),
            crawl_sitemap_only=bool(args.crawl_sitemap_only),
            tag=args.tag,
        )
        print(f"OnPage task created: {task_id} (target={target}, max_crawl_pages={args.max_crawl_pages})", flush=True)

    # Poll until finished
    start = time.time()
    summary_obj: dict = {}
    while True:
        summary_obj = onpage_summary(login=login, password=password, task_id=task_id)
        progress = (summary_obj.get("crawl_progress") or "").strip().lower()
        status_code = str(summary_obj.get("_status_code") or "")
        status_message = str(summary_obj.get("_status_message") or "")
        crawl_status = summary_obj.get("crawl_status") or {}
        pages_crawled = crawl_status.get("pages_crawled", "")
        pages_in_queue = crawl_status.get("pages_in_queue", "")
        if progress:
            print(f"crawl_progress={progress} crawled={pages_crawled} in_queue={pages_in_queue}", flush=True)
        else:
            print(f"summary_status_code={status_code} message={status_message}", flush=True)

        # Eventual consistency right after task creation
        if status_code == "40401":
            time.sleep(max(5, int(args.poll_seconds)))
            continue
        if progress == "finished":
            break
        if (time.time() - start) > max(30, int(args.max_wait_seconds)):
            raise SystemExit(f"OnPage crawl still in_progress after {args.max_wait_seconds}s (task_id={task_id}).")
        time.sleep(max(3, int(args.poll_seconds)))

    # Export Summary + IssueCounts (from page_metrics.checks)
    domain_info = summary_obj.get("domain_info") or {}
    page_metrics = summary_obj.get("page_metrics") or {}
    checks_counts = (page_metrics.get("checks") or {}) if isinstance(page_metrics.get("checks"), dict) else {}

    summary_rows = [
        {"section": "OnPage", "metric": "task_id", "value": task_id, "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "target", "value": target, "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "total_pages", "value": domain_info.get("total_pages", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "onpage_score", "value": page_metrics.get("onpage_score", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "non_indexable", "value": page_metrics.get("non_indexable", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "duplicate_title", "value": page_metrics.get("duplicate_title", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "duplicate_description", "value": page_metrics.get("duplicate_description", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "duplicate_content", "value": page_metrics.get("duplicate_content", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "broken_links", "value": page_metrics.get("broken_links", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "broken_resources", "value": page_metrics.get("broken_resources", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "crawl_start", "value": domain_info.get("crawl_start", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "crawl_end", "value": domain_info.get("crawl_end", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "cms", "value": domain_info.get("cms", ""), "fetched_at": fetched_at},
        {"section": "OnPage", "metric": "server", "value": domain_info.get("server", ""), "fetched_at": fetched_at},
    ]
    write_csv(
        os.path.join(args.output_dir, "Benchmark_OnPage_Summary.csv"),
        ["section", "metric", "value", "fetched_at"],
        summary_rows,
    )

    issue_rows = [
        {"check": k, "count": v, "fetched_at": fetched_at}
        for k, v in sorted(checks_counts.items(), key=lambda kv: (-float(kv[1] or 0), kv[0]))
    ]
    write_csv(
        os.path.join(args.output_dir, "Benchmark_OnPage_IssueCounts.csv"),
        ["check", "count", "fetched_at"],
        issue_rows,
    )

    # Export Pages (paged)
    pages_out: List[Dict[str, object]] = []
    limit = 200
    offset = 0
    export_cap = max(1, int(args.export_pages))
    while len(pages_out) < export_cap:
        res = onpage_pages(login=login, password=password, task_id=task_id, limit=limit, offset=offset)
        items = res.get("items") or []
        if not items:
            break
        for it in items:
            meta = it.get("meta") or {}
            checks = it.get("checks") or {}
            pages_out.append(
                {
                    "url": it.get("url", ""),
                    "status_code": it.get("status_code", ""),
                    "click_depth": it.get("click_depth", ""),
                    "from_sitemap": (checks.get("from_sitemap") if isinstance(checks, dict) else ""),
                    "canonical": meta.get("canonical", ""),
                    "title_length": meta.get("title_length", ""),
                    "description_length": meta.get("description_length", ""),
                    "internal_links_count": meta.get("internal_links_count", ""),
                    "inbound_links_count": meta.get("inbound_links_count", ""),
                    "is_broken": (checks.get("is_broken") if isinstance(checks, dict) else ""),
                    "is_redirect": (checks.get("is_redirect") if isinstance(checks, dict) else ""),
                    "is_4xx_code": (checks.get("is_4xx_code") if isinstance(checks, dict) else ""),
                    "is_5xx_code": (checks.get("is_5xx_code") if isinstance(checks, dict) else ""),
                    "no_title": (checks.get("no_title") if isinstance(checks, dict) else ""),
                    "no_description": (checks.get("no_description") if isinstance(checks, dict) else ""),
                    "title_too_long": (checks.get("title_too_long") if isinstance(checks, dict) else ""),
                    "title_too_short": (checks.get("title_too_short") if isinstance(checks, dict) else ""),
                    "duplicate_title": it.get("duplicate_title", ""),
                    "duplicate_description": it.get("duplicate_description", ""),
                    "duplicate_content": it.get("duplicate_content", ""),
                    "fetched_at": fetched_at,
                }
            )
            if len(pages_out) >= export_cap:
                break
        offset += limit

    write_csv(
        os.path.join(args.output_dir, "Benchmark_OnPage_Pages.csv"),
        [
            "url",
            "status_code",
            "click_depth",
            "from_sitemap",
            "canonical",
            "title_length",
            "description_length",
            "internal_links_count",
            "inbound_links_count",
            "is_broken",
            "is_redirect",
            "is_4xx_code",
            "is_5xx_code",
            "no_title",
            "no_description",
            "title_too_long",
            "title_too_short",
            "duplicate_title",
            "duplicate_description",
            "duplicate_content",
            "fetched_at",
        ],
        pages_out,
    )

    # Export Non-indexable (paged)
    nonidx_out: List[Dict[str, object]] = []
    limit = 500
    offset = 0
    cap = max(1, int(args.export_nonindexable))
    while len(nonidx_out) < cap:
        res = onpage_non_indexable(login=login, password=password, task_id=task_id, limit=limit, offset=offset)
        items = res.get("items") or []
        if not items:
            break
        for it in items:
            nonidx_out.append({"reason": it.get("reason", ""), "url": it.get("url", ""), "fetched_at": fetched_at})
            if len(nonidx_out) >= cap:
                break
        offset += limit

    write_csv(
        os.path.join(args.output_dir, "Benchmark_OnPage_NonIndexable.csv"),
        ["reason", "url", "fetched_at"],
        nonidx_out,
    )

    print("OK")
    print("task_id:", task_id)
    print("wrote: Benchmark_OnPage_Summary.csv")
    print("wrote: Benchmark_OnPage_IssueCounts.csv")
    print("wrote: Benchmark_OnPage_Pages.csv")
    print("wrote: Benchmark_OnPage_NonIndexable.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

