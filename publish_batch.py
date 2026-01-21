#!/usr/bin/env python3
"""
Publish a batch of content items using the canonical pipeline.

Typical monthly usage:
  python3 publish_batch.py /Users/jasonmellet/Desktop/AGT_Camp_Lakota/content/posts --type posts
  python3 publish_batch.py /Users/jasonmellet/Desktop/AGT_Camp_Lakota/content/pages --type pages

Or provide individual files:
  python3 publish_batch.py /abs/path/a.json /abs/path/b.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agt_publisher_core.client_config import load_client_config
from agt_publisher_core.config import Config
from agt_publisher_core.modules.auth import WordPressAuth
from agt_publisher_core.modules.publish_pipeline import PublishOptions, PublishPipeline
from agt_publisher_core.preflight import run_publish_preflight

console = Console()


def _collect_files(inputs: list[str]) -> list[str]:
    out: list[str] = []
    for p in inputs:
        path = Path(p)
        if path.is_dir():
            out.extend([str(x) for x in sorted(path.glob("*.json")) if "example" not in x.name.lower()])
        else:
            out.append(str(path))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="JSON file(s) or directory(ies) containing JSON files")
    parser.add_argument("--type", choices=["posts", "pages"], default=None, help="Override type inference for all items")
    parser.add_argument("--status", choices=["draft", "publish"], default="draft")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts (for automation)")
    parser.add_argument("--resolve-links", action="store_true")
    parser.add_argument("--enable-toc", action="store_true")
    parser.add_argument("--no-acf", action="store_true")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first validation failure")
    args = parser.parse_args()

    Config.validate()
    client = load_client_config()

    console.print(Panel.fit("[bold cyan]Publish Batch[/bold cyan]\n[dim]Canonical pipeline[/dim]", border_style="cyan"))

    files = _collect_files(args.paths)
    if not files:
        console.print("[red]No JSON files found.[/red]")
        return 2

    auth = WordPressAuth()
    ok, msg, data = auth.test_connection()
    if not ok:
        console.print(f"[red]Connection failed:[/red] {msg}")
        return 2
    detected_site_name = (data or {}).get("site_name") if isinstance(data, dict) else None
    run_publish_preflight(client=client, detected_site_name=detected_site_name, status=args.status, assume_yes=args.yes)

    session = auth.get_session()
    pipeline = PublishPipeline(session, client=client)

    options = PublishOptions(
        status=args.status,
        resolve_links=args.resolve_links,
        enable_toc=args.enable_toc,
        use_acf_blocks=(not args.no_acf),
    )

    results = []
    for f in files:
        wp_id, validation = pipeline.publish_from_file(f, content_type=args.type, options=options)
        results.append((f, wp_id, validation))
        if args.fail_fast and (wp_id is None or not validation.ok):
            break

    table = Table(title="Batch Results")
    table.add_column("File", style="cyan")
    table.add_column("WP ID", style="green")
    table.add_column("OK", style="green")
    table.add_column("Errors", style="red")
    table.add_column("Warnings", style="yellow")

    ok_count = 0
    for f, wp_id, v in results:
        ok_flag = "yes" if (v.ok and (wp_id is not None or Config.is_dry_run())) else "no"
        if ok_flag == "yes":
            ok_count += 1
        table.add_row(
            Path(f).name,
            str(wp_id or ""),
            ok_flag,
            str(len(v.errors)),
            str(len(v.warnings)),
        )

    console.print(table)
    console.print(f"\n[bold]OK:[/bold] {ok_count}/{len(results)}")

    any_failed = any((wp_id is None and not Config.is_dry_run()) or (not v.ok) for _, wp_id, v in results)
    if any_failed:
        console.print("\n[bold yellow]Some items failed validation and were left as drafts.[/bold yellow]")
        return 3
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        raise SystemExit(130)

