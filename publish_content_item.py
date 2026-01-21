#!/usr/bin/env python3
"""
Publish ONE content item (blog post or landing page) using the canonical pipeline.

This is the script you should use monthly. It enforces:
- consistent spacing
- optional TOC (auto for long posts)
- media rules (featured image selection + body images)
- Yoast SEO meta
- immediate verification gates (FAQ count, image count, etc.)

Usage:
  python3 publish_content_item.py /abs/path/to/content/posts/my-post.json --type posts
  python3 publish_content_item.py /abs/path/to/content/pages/my-page.json --type pages
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from agt_publisher_core.client_config import load_client_config
from agt_publisher_core.config import Config
from agt_publisher_core.modules.auth import WordPressAuth
from agt_publisher_core.modules.publish_pipeline import PublishOptions, PublishPipeline
from agt_publisher_core.preflight import run_publish_preflight

console = Console()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="Absolute path to the content JSON file")
    parser.add_argument("--type", choices=["posts", "pages"], default=None, help="Override content type inference")
    parser.add_argument("--status", choices=["draft", "publish"], default="draft", help="WP status (default draft)")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts (for automation)")
    parser.add_argument("--resolve-links", action="store_true", help="Resolve {{link:...}} placeholders using current WP slug map")
    parser.add_argument("--enable-toc", action="store_true", help="Force enable TOC for posts")
    parser.add_argument("--no-acf", action="store_true", help="Disable ACF block conversion for pages")
    parser.add_argument("--min-images", type=int, default=2, help="Minimum content images for posts (default 2)")
    parser.add_argument("--max-images", type=int, default=4, help="Maximum content images for posts (default 4)")
    parser.add_argument("--faq-questions", type=int, default=0, help="Enforce exact FAQ question count (0 disables; default 0)")
    args = parser.parse_args()

    Config.validate()
    client = load_client_config()

    options = PublishOptions(
        status=args.status,
        resolve_links=args.resolve_links,
        enable_toc=args.enable_toc,
        min_content_images=args.min_images,
        max_content_images=args.max_images,
        required_faq_questions=(None if args.faq_questions == 0 else args.faq_questions),
        use_acf_blocks=(not args.no_acf),
    )

    console.print(Panel.fit("[bold cyan]Publish Content Item[/bold cyan]\n[dim]Canonical pipeline[/dim]", border_style="cyan"))
    console.print(f"[dim]Source: {args.source_file}[/dim]")
    console.print(f"[dim]Type: {args.type or '(auto)'} | Status: {args.status}[/dim]\n")

    auth = WordPressAuth()
    ok, msg, data = auth.test_connection()
    if not ok:
        console.print(f"[red]Connection failed:[/red] {msg}")
        return 2
    # Wrong-site guardrail + publish confirmation
    detected_site_name = (data or {}).get("site_name") if isinstance(data, dict) else None
    run_publish_preflight(client=client, detected_site_name=detected_site_name, status=args.status, assume_yes=args.yes)

    session = auth.get_session()
    pipeline = PublishPipeline(session, client=client)

    wp_id, validation = pipeline.publish_from_file(args.source_file, content_type=args.type, options=options)

    if wp_id is None:
        if Config.is_dry_run() and validation.ok:
            console.print("\n[bold green]✓ DRY RUN complete (no WordPress writes)[/bold green]")
            for w in validation.warnings:
                console.print(f"[yellow]- {w}[/yellow]")
            return 0
        console.print("\n[bold red]✗ Publish failed[/bold red]")
        for e in validation.errors:
            console.print(f"[red]- {e}[/red]")
        for w in validation.warnings:
            console.print(f"[yellow]- {w}[/yellow]")
        return 2

    if validation.ok:
        console.print(f"\n[bold green]✓ Published/Updated successfully (ID: {wp_id})[/bold green]")
        for w in validation.warnings:
            console.print(f"[yellow]- {w}[/yellow]")
        return 0

    console.print(f"\n[bold red]✗ Published but FAILED validation gates (ID: {wp_id})[/bold red]")
    for e in validation.errors:
        console.print(f"[red]- {e}[/red]")
    for w in validation.warnings:
        console.print(f"[yellow]- {w}[/yellow]")
    console.print("\n[yellow]Left as draft; fix source and re-run this script.[/yellow]")
    return 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        raise SystemExit(130)

