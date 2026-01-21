#!/usr/bin/env python3
"""
Resolve all internal link placeholders in blog posts and landing pages
Replaces {{link:slug|text}} with actual WordPress URLs
"""

import argparse
import re

from config import Config
from modules.auth import WordPressAuth
from modules.links import InternalLinkManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agt_publisher_core.client_config import load_client_config
from agt_publisher_core.preflight import run_publish_preflight

console = Console()


def find_all_placeholders(content):
    """Find all link placeholders in content"""
    pattern = r'\{\{link:([^|}]+)(?:\|[^}]+)?\}\}'
    matches = re.findall(pattern, content)
    return [slug.strip() for slug in matches]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-drafts", action="store_true", help="Also update drafts (default: publish-only)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes; only report")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override link map entry: slug=url (repeatable). Example: --override contact=https://example.com/contact/",
    )
    parser.add_argument(
        "--rewrite-url",
        action="append",
        default=[],
        help="Rewrite existing href targets: from_url=to_url (repeatable). Example: --rewrite-url https://old/=https://new/",
    )
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]Resolve Internal Links in All Content[/bold cyan]\n"
        "[dim]Publish-only by default; safe replacement inside href=\"...\"[/dim]",
        border_style="cyan"
    ))
    
    Config.validate()
    client = load_client_config()
    auth = WordPressAuth()
    ok, msg, data = auth.test_connection()
    if not ok:
        raise SystemExit(f"Connection failed: {msg}")
    detected_site_name = (data or {}).get("site_name") if isinstance(data, dict) else None
    # Wrong-site guardrail for this write operation (no publish prompt; still enforces URL/host match)
    run_publish_preflight(client=client, detected_site_name=detected_site_name, status="draft", assume_yes=True)

    session = auth.get_session()
    link_manager = InternalLinkManager(session, link_aliases=(client.linkAliases or None))
    
    # Step 1: Build link map
    console.print("\n[bold]Step 1: Building Link Map[/bold]")
    console.print("[cyan]Building link map from WordPress content...[/cyan]")
    link_map = link_manager.build_slug_map()
    console.print(f"[green]✓[/green] Built link map with {len(link_map)} entries\n")

    # Apply overrides
    overrides = {}
    for ov in args.override:
        if "=" not in ov:
            continue
        slug, url = ov.split("=", 1)
        slug = slug.strip()
        url = url.strip()
        if slug and url:
            overrides[slug] = url
    if overrides:
        link_map.update(overrides)
        console.print(f"[green]✓[/green] Applied {len(overrides)} override(s)\n")

    # Prepare rewrite rules
    rewrites = []
    for rw in args.rewrite_url:
        if "=" not in rw:
            continue
        src, dst = rw.split("=", 1)
        src = src.strip()
        dst = dst.strip()
        if src and dst:
            rewrites.append((src, dst))


    if not link_map:
        console.print("[red]No content found to build link map![/red]")
        return
    
    # Step 2: Find all content with placeholders
    console.print("\n[bold]Step 2: Finding Content with Link Placeholders[/bold]")
    
    status_filter = "any" if args.include_drafts else "publish"

    # Get all pages
    pages_to_update = []
    page = 1
    while True:
        response = session.get(
            Config.get_api_url('pages'),
            params={
                'per_page': 100,
                'page': page,
                'status': status_filter,
                'context': 'edit'
            },
            timeout=30
        )
        if response.status_code != 200:
            break
        batch = response.json()
        if not batch:
            break
        
        for page_item in batch:
            content = page_item.get('content', {}).get('raw', '')
            placeholders = find_all_placeholders(content)
            if placeholders:
                pages_to_update.append({
                    'id': page_item['id'],
                    'slug': page_item.get('slug', ''),
                    'title': page_item.get('title', {}).get('rendered', ''),
                    'content': content,
                    'placeholders': placeholders
                })
        page += 1
    
    # Get all posts
    posts_to_update = []
    page = 1
    while True:
        response = session.get(
            Config.get_api_url('posts'),
            params={
                'per_page': 100,
                'page': page,
                'status': status_filter,
                'context': 'edit'
            },
            timeout=30
        )
        if response.status_code != 200:
            break
        batch = response.json()
        if not batch:
            break
        
        for post_item in batch:
            content = post_item.get('content', {}).get('raw', '')
            placeholders = find_all_placeholders(content)
            if placeholders:
                posts_to_update.append({
                    'id': post_item['id'],
                    'slug': post_item.get('slug', ''),
                    'title': post_item.get('title', {}).get('rendered', ''),
                    'content': content,
                    'placeholders': placeholders
                })
        page += 1
    
    # Display summary
    summary_table = Table(title="Content with Link Placeholders")
    summary_table.add_column("Type", style="cyan")
    summary_table.add_column("Title", style="yellow")
    summary_table.add_column("ID", style="dim")
    summary_table.add_column("Placeholders", style="green")
    
    for item in pages_to_update:
        summary_table.add_row(
            "Page",
            item['title'][:50] + '...' if len(item['title']) > 50 else item['title'],
            str(item['id']),
            str(len(item['placeholders']))
        )
    
    for item in posts_to_update:
        summary_table.add_row(
            "Post",
            item['title'][:50] + '...' if len(item['title']) > 50 else item['title'],
            str(item['id']),
            str(len(item['placeholders']))
        )
    
    console.print(summary_table)
    
    total_items = len(pages_to_update) + len(posts_to_update)
    if total_items == 0:
        console.print("\n[green]✓[/green] No content with link placeholders found!")
        return
    
    # Step 3: Resolve and update links
    console.print(f"\n[bold]Step 3: Resolving Links in {total_items} Items[/bold]\n")
    if args.dry_run:
        console.print("[yellow]DRY RUN enabled: no changes will be written.[/yellow]\n")
    
    results_table = Table(title="Link Resolution Results")
    results_table.add_column("Type", style="cyan")
    results_table.add_column("Title", style="yellow")
    results_table.add_column("ID", style="dim")
    results_table.add_column("Links Resolved", style="green")
    results_table.add_column("Status", style="dim")
    
    success_count = 0
    
    # Update pages
    for item in pages_to_update:
        updated_content = link_manager.replace_link_placeholders(item['content'], link_map)
        for src, dst in rewrites:
            updated_content = updated_content.replace(src, dst)
        
        if updated_content != item['content']:
            if args.dry_run:
                status = "🟡 Would update"
            else:
                response = session.post(
                    Config.get_api_url(f"pages/{item['id']}"),
                    json={'content': updated_content},
                    timeout=30
                )
                
                if response.status_code == 200:
                    status = "✅ Updated"
                    success_count += 1
                else:
                    status = f"❌ Failed ({response.status_code})"
        else:
            status = "⚠️ No changes"
        
        results_table.add_row(
            "Page",
            item['title'][:40] + '...' if len(item['title']) > 40 else item['title'],
            str(item['id']),
            str(len(item['placeholders'])),
            status
        )
    
    # Update posts
    for item in posts_to_update:
        updated_content = link_manager.replace_link_placeholders(item['content'], link_map)
        for src, dst in rewrites:
            updated_content = updated_content.replace(src, dst)
        
        if updated_content != item['content']:
            if args.dry_run:
                status = "🟡 Would update"
            else:
                response = session.post(
                    Config.get_api_url(f"posts/{item['id']}"),
                    json={'content': updated_content},
                    timeout=30
                )
                
                if response.status_code == 200:
                    status = "✅ Updated"
                    success_count += 1
                else:
                    status = f"❌ Failed ({response.status_code})"
        else:
            status = "⚠️ No changes"
        
        results_table.add_row(
            "Post",
            item['title'][:40] + '...' if len(item['title']) > 40 else item['title'],
            str(item['id']),
            str(len(item['placeholders'])),
            status
        )
    
    console.print("\n")
    console.print(results_table)
    
    # Summary
    console.print(f"\n[bold green]✅ Link Resolution Complete![/bold green]")
    if args.dry_run:
        console.print(f"  • DRY RUN: {total_items} items analyzed (no writes)")
    else:
        console.print(f"  • {success_count} of {total_items} items updated")
    console.print(f"\n[bold]Next Steps:[/bold]")
    console.print(f"  1. Preview content in WordPress to verify links work")
    console.print(f"  2. Check for any missing links (warnings above)")
    console.print(f"  3. Ready for final review and publishing!")


if __name__ == '__main__':
    main()
