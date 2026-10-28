#!/usr/bin/env python3
"""
HogEye internal link deep dive (map → checklist gaps → optional OpenAI recommendations).

Phase 1 — deterministic (no OpenAI):
  - Paginates WordPress REST `posts` + `pages` (published by default).
  - Extracts <a href> from `content.rendered`, resolves relative URLs, keeps same-site links only.
  - Writes JSON graph + CSV edges + summary markdown.
  - Compares `PROJECT_CONFIG.json` internal_links.targets to measured inbound links (coverage).

Phase 2 — optional SEO analysis:
  - Sends a compact summary + allowlisted URLs to OpenAI (default model: OPENAI_MODEL or gpt-5.4).
  - Model must not invent URLs; recommendations reference allowlist + graph only.

Usage:
  ./.venv/bin/python scripts/seo/hogeye_internal_link_deep_dive.py \\
    --project-root "$(pwd)" \\
    --output-dir workspace/ops/internal_link_deep_dive/latest

  ./.venv/bin/python scripts/seo/hogeye_internal_link_deep_dive.py ... --openai-analysis
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from dotenv import load_dotenv

from repo_workspace import workspace_dir_under, workspace_rel_posix

_WS_DEFAULT_OUT = Path(workspace_rel_posix()) / "ops/internal_link_deep_dive/latest"


def _host_identity(host: str) -> str:
    """Lowercase host with leading www. removed — compares hogeye.com vs www.hogeye.com."""
    h = (host or "").strip().lower()
    if h.startswith("www."):
        return h[4:]
    return h


def canonical_site_parts(site: str) -> Tuple[str, str]:
    """
    Scheme + netloc from WP_SITE_URL (authoritative for all normalized URLs).
    Example: https://hogeyecameras.com -> ("https", "hogeyecameras.com")
    """
    s = (site or "").strip().rstrip("/")
    if not s:
        return "https", ""
    if "://" not in s:
        s = "https://" + s
    p = urlparse(s)
    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower()
    return scheme, netloc


def normalize_internal_url(
    url: str,
    *,
    canonical_scheme: str,
    canonical_netloc: str,
    lowercase_path: bool = True,
) -> str:
    """
    Canonical same-site URL for edges, page keys, and PROJECT_CONFIG targets.

    - Strips #fragments (not sent to server)
    - Unifies www / non-www to canonical_netloc from WP_SITE_URL
    - Strips trailing slash on non-root paths
    - Lowercases path segments by default (WordPress permalinks)
    """
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith(("#", "mailto:", "tel:", "javascript:")):
        return ""
    if "://" not in url and url.startswith("/"):
        url = f"{canonical_scheme}://{canonical_netloc}{url}"
    p = urlparse(url)
    if p.scheme not in ("http", "https", ""):
        return ""
    host = (p.netloc or "").lower()
    if not host:
        return ""
    if _host_identity(host) != _host_identity(canonical_netloc):
        return ""

    path = p.path or "/"
    if path != "/":
        segs = [s for s in path.split("/") if s]
        if lowercase_path:
            segs = [s.lower() for s in segs]
        path = "/" + "/".join(segs)
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    query = f"?{p.query}" if p.query else ""
    return f"{canonical_scheme}://{canonical_netloc}{path}{query}"


def _resolve_and_normalize_href(
    href: str,
    base_page: str,
    *,
    canonical_scheme: str,
    canonical_netloc: str,
    lowercase_path: bool,
) -> str:
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return ""
    joined = urljoin(base_page, href)
    return normalize_internal_url(
        joined,
        canonical_scheme=canonical_scheme,
        canonical_netloc=canonical_netloc,
        lowercase_path=lowercase_path,
    )


class _HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "a":
            return
        ad = {k.lower(): v for k, v in attrs if k}
        href = ad.get("href")
        if href:
            self.hrefs.append(href.strip())


def _load_project_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _fetch_all(
    session: requests.Session,
    api_base: str,
    kind: str,
    *,
    status: str,
    per_page: int = 100,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = session.get(
            f"{api_base}/wp/v2/{kind}",
            params={"per_page": per_page, "page": page, "status": status, "context": "view"},
            timeout=45,
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        page += 1
    return out


def _extract_links_from_html(
    html: str,
    page_url: str,
    *,
    canonical_scheme: str,
    canonical_netloc: str,
    lowercase_path: bool,
) -> List[str]:
    parser = _HrefCollector()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        return []
    out: List[str] = []
    seen: Set[str] = set()
    for h in parser.hrefs:
        n = _resolve_and_normalize_href(
            h,
            page_url,
            canonical_scheme=canonical_scheme,
            canonical_netloc=canonical_netloc,
            lowercase_path=lowercase_path,
        )
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _openai_analyze(
    *,
    api_key: str,
    model: str,
    site: str,
    summary: Dict[str, Any],
    allowlist_urls: List[str],
) -> str:
    import urllib.request

    system = (
        "You are an SEO internal linking analyst for one website. "
        "You only reference URLs that appear in the provided allowlist or in the graph summary. "
        "Never invent pages or URLs. If data is missing, say what to collect next. "
        "Output Markdown with: Executive summary, Coverage vs priority targets, Gaps, "
        "Recommended new internal links (source page → target page + anchor idea), "
        "and a 30-day link-building plan (bullet list). "
        "Stay aligned to wild hog trap monitoring / wild hog trap camera system positioning when relevant. "
        "Do not recommend internal links to login, account, or wp-admin URLs unless the operator explicitly asks."
    )
    user = (
        f"Site: {site}\n\n"
        f"Graph summary (JSON):\n{json.dumps(summary, indent=2)[:120000]}\n\n"
        f"Allowlisted URLs ({len(allowlist_urls)}):\n"
        + "\n".join(allowlist_urls[:2000])
    )
    payload = json.dumps(
        {
            "model": model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["choices"][0]["message"]["content"] or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Internal link map + optional OpenAI SEO analysis (HogEye)")
    ap.add_argument("--project-root", default=str(Path.cwd()), type=Path)
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=_WS_DEFAULT_OUT,
        help="Directory for JSON/CSV/MD outputs",
    )
    ap.add_argument("--status", default="publish", help="WP status filter (default: publish)")
    ap.add_argument("--include-drafts", action="store_true", help="Use status=any (includes drafts)")
    ap.add_argument("--openai-analysis", action="store_true", help="Run OpenAI on summary + allowlist")
    ap.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "").strip() or "gpt-5.4",
        help="Chat model for --openai-analysis (override with OPENAI_MODEL)",
    )
    ap.add_argument(
        "--preserve-path-case",
        action="store_true",
        help="Do not lowercase URL path segments (default: lowercase for stable matching)",
    )
    args = ap.parse_args()

    root = args.project_root.resolve()
    load_dotenv(root / ".env", override=False)
    site = (os.environ.get("WP_SITE_URL") or "").strip().rstrip("/")
    user = (os.environ.get("WP_USERNAME") or "").strip()
    password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not site or not user or not password:
        print("Missing WP_SITE_URL / WP_USERNAME / WP_APP_PASSWORD in .env", flush=True)
        return 2

    canonical_scheme, canonical_netloc = canonical_site_parts(site)
    if not canonical_netloc:
        print("WP_SITE_URL must include a hostname (e.g. https://hogeyecameras.com)", flush=True)
        return 2
    lowercase_path = not args.preserve_path_case

    wp_json = f"{site}/wp-json"
    session = requests.Session()
    session.auth = (user, password)
    session.headers.update(
        {
            "User-Agent": "HogEye-InternalLinkDeepDive/1.0",
            "Accept": "application/json",
        }
    )

    status = "any" if args.include_drafts else args.status
    items: List[Dict[str, Any]] = []
    items.extend(_fetch_all(session, wp_json, "posts", status=status))
    items.extend(_fetch_all(session, wp_json, "pages", status=status))

    edges: List[Dict[str, str]] = []
    page_meta: Dict[str, Dict[str, Any]] = {}

    for it in items:
        link = (it.get("link") or "").strip()
        if not link:
            continue
        link_key = normalize_internal_url(
            link,
            canonical_scheme=canonical_scheme,
            canonical_netloc=canonical_netloc,
            lowercase_path=lowercase_path,
        )
        if not link_key:
            continue
        title = it.get("title") or {}
        if isinstance(title, dict):
            title_s = (title.get("rendered") or title.get("raw") or "").strip()
        else:
            title_s = str(title)
        content = it.get("content") or {}
        html = ""
        if isinstance(content, dict):
            html = content.get("rendered") or content.get("raw") or ""
        slug = (it.get("slug") or "").strip()
        kind = "post" if it.get("type") == "post" else "page"
        if link_key in page_meta:
            continue
        page_meta[link_key] = {
            "slug": slug,
            "title": re.sub(r"<[^>]+>", "", title_s),
            "type": kind,
            "wp_id": it.get("id"),
            "permalink_raw": link,
        }
        for to_u in _extract_links_from_html(
            html,
            link_key,
            canonical_scheme=canonical_scheme,
            canonical_netloc=canonical_netloc,
            lowercase_path=lowercase_path,
        ):
            edges.append({"from_url": link_key, "to_url": to_u, "anchor_context": "in_body"})

    out_deg = Counter(e["from_url"] for e in edges)
    in_deg = Counter(e["to_url"] for e in edges)

    cfg_path = workspace_dir_under(root) / "PROJECT_CONFIG.json"
    cfg = _load_project_config(cfg_path)
    priority_targets: List[str] = []
    il = cfg.get("internal_links") if isinstance(cfg, dict) else None
    if isinstance(il, dict):
        for u in il.get("targets") or []:
            raw = str(u).strip()
            if not raw:
                continue
            nu = normalize_internal_url(
                raw,
                canonical_scheme=canonical_scheme,
                canonical_netloc=canonical_netloc,
                lowercase_path=lowercase_path,
            )
            if nu:
                priority_targets.append(nu)
            else:
                joined = raw if raw.startswith("http") else f"{canonical_scheme}://{canonical_netloc}{raw if raw.startswith('/') else '/' + raw}"
                nu2 = normalize_internal_url(
                    joined,
                    canonical_scheme=canonical_scheme,
                    canonical_netloc=canonical_netloc,
                    lowercase_path=lowercase_path,
                )
                if nu2:
                    priority_targets.append(nu2)

    priority_targets = list(dict.fromkeys(priority_targets))

    coverage: Dict[str, Dict[str, Any]] = {}
    for t in priority_targets:
        inbound = [e["from_url"] for e in edges if e["to_url"] == t]
        coverage[t] = {"inbound_count": len(set(inbound)), "from_pages_sample": list(dict.fromkeys(inbound))[:15]}

    orphans = [u for u in page_meta if in_deg[u] == 0 and out_deg[u] == 0]
    top_out = out_deg.most_common(25)
    top_in = in_deg.most_common(25)

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "site": site,
        "url_normalization": {
            "canonical_scheme": canonical_scheme,
            "canonical_host": canonical_netloc,
            "www_unification": "same host with or without www maps to canonical_host from WP_SITE_URL",
            "trailing_slash": "stripped on non-root paths",
            "fragments": "stripped",
            "path_segments": "lowercased" if lowercase_path else "preserved",
        },
        "status_filter": status,
        "page_count": len(page_meta),
        "edge_count": len(edges),
        "unique_targets_linked_to": len(in_deg),
        "priority_targets": priority_targets,
        "priority_target_coverage": coverage,
        "hubs_out_degree_top": [{"url": u, "out": c} for u, c in top_out],
        "authority_in_degree_top": [{"url": u, "in": c} for u, c in top_in],
        "orphan_urls_no_in_no_out": sorted(orphans)[:200],
    }

    out_dir = (root / args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = out_dir / "internal_link_graph.json"
    graph_path.write_text(
        json.dumps({"pages": page_meta, "edges": edges, "summary": summary}, indent=2),
        encoding="utf-8",
    )

    csv_path = out_dir / "internal_link_edges.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from_url", "to_url", "anchor_context"])
        w.writeheader()
        for row in edges:
            w.writerow(row)

    md_lines = [
        f"# Internal link map — {site}",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Pages/posts scanned: **{len(page_meta)}**",
        f"- Internal edges (same-site `<a href>`): **{len(edges)}**",
        "",
        "## Priority targets (PROJECT_CONFIG) — inbound coverage",
        "",
    ]
    for t in priority_targets:
        c = coverage.get(t, {})
        md_lines.append(f"- `{t}` — **{c.get('inbound_count', 0)}** unique referring pages")
    md_lines.extend(
        [
            "",
            "## Top outbound hubs (pages linking out the most)",
            "",
        ]
    )
    for u, c in top_out[:15]:
        md_lines.append(f"- `{u}` — {c} outbound internal links")
    try:
        rel = lambda p: str(p.resolve().relative_to(root))  # noqa: E731
        file_section = [
            "",
            "## Files",
            "",
            f"- Graph: `{rel(graph_path)}`",
            f"- CSV: `{rel(csv_path)}`",
            "",
        ]
    except ValueError:
        file_section = ["", "## Files", "", f"- `{graph_path.name}`", f"- `{csv_path.name}`", ""]

    report_path = out_dir / "INTERNAL_LINK_MAP_REPORT.md"
    report_path.write_text("\n".join(md_lines + file_section), encoding="utf-8")

    print(f"Wrote {graph_path}", flush=True)
    print(f"Wrote {csv_path}", flush=True)
    print(f"Wrote {report_path}", flush=True)

    if args.openai_analysis:
        api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
        if not api_key:
            print("OPENAI_API_KEY missing; skipping OpenAI analysis.", flush=True)
            return 2
        allowlist = sorted(set(page_meta.keys()) | set(in_deg.keys()) | set(out_deg.keys()) | set(priority_targets))
        analysis = _openai_analyze(
            api_key=api_key,
            model=args.model,
            site=site,
            summary=summary,
            allowlist_urls=allowlist,
        )
        analysis_path = out_dir / "SEO_INTERNAL_LINK_ANALYSIS.md"
        analysis_path.write_text(analysis + "\n", encoding="utf-8")
        print(f"Wrote {analysis_path}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
