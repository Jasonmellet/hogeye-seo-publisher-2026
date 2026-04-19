#!/usr/bin/env python3
"""
Process Landing Page - Complete Workflow:
1. Check if page exists
2. Duplicate it
3. Clear all content in duplicate
4. Add new formatted content
5. Set to draft
6. Provide instructions for swapping
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

from modules.publish_pipeline import PublishOptions, PublishPipeline
from modules.source_loader import load_content_file


def process_landing_page(json_file: str, temp_slug_suffix: str = '-draft-review'):
    """Complete landing page processing workflow"""
    
    console.print(Panel.fit("[bold cyan]Landing Page Processing Workflow[/bold cyan]"))
    
    console.print(f"\n[cyan]Step 1: Loading source content from {json_file}...[/cyan]")
    loaded = load_content_file(json_file)
    source_data = loaded.data
    target_slug = source_data.get("slug", "unknown")
    console.print(f"[green]✓[/green] Loaded content for slug: {target_slug}")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    pipeline = PublishPipeline(session)
    
    # Step 2: Check if page exists
    console.print(f"\n[cyan]Step 2: Checking if page exists (slug: {target_slug})...[/cyan]")
    
    response = session.get(
        Config.get_api_url('pages'),
        params={'slug': target_slug, 'per_page': 100, 'status': 'any'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error checking page: {response.status_code}[/red]")
        return
    
    pages = response.json()
    original_page = None
    for page in pages:
        if page.get('slug') == target_slug:
            original_page = page
            break
    
    if not original_page:
        console.print(f"[yellow]⚠[/yellow] Page doesn't exist - will create new page")
        original_id = None
    else:
        original_id = original_page['id']
        console.print(f"[green]✓[/green] Found existing page ID: {original_id}")
        console.print(f"  Title: {original_page.get('title', {}).get('rendered', 'N/A')}")
        console.print(f"  Status: {original_page.get('status', 'N/A')}")
        console.print(f"  URL: {original_page.get('link', 'N/A')}")
    
    # Step 3: Duplicate the page (or create new)
    console.print(f"\n[cyan]Step 3: Creating duplicate with temp slug...[/cyan]")
    
    temp_slug = target_slug + temp_slug_suffix
    
    if original_page:
        # Duplicate existing page
        duplicate_data = {
            'title': original_page.get('title', {}).get('rendered', '') + ' (Draft Review)',
            'slug': temp_slug,
            'content': '',  # Clear all content
            'excerpt': '',
            'status': 'draft',
            'meta': original_page.get('meta', {})
        }
    else:
        # Create new page
        duplicate_data = {
            'title': source_data.get('title', '') + ' (Draft Review)',
            'slug': temp_slug,
            'content': '',  # Will add content in next step
            'excerpt': '',
            'status': 'draft',
            'meta': {}
        }
    
    response = session.post(
        Config.get_api_url('pages'),
        json=duplicate_data,
        timeout=30
    )
    
    if response.status_code not in [200, 201]:
        console.print(f"[red]Error creating duplicate: {response.status_code}[/red]")
        console.print(response.text[:500])
        return
    
    # Handle PHP warnings in response
    try:
        duplicate_page = response.json()
    except:
        # Page was created but response has PHP warnings - find it by slug
        response = session.get(
            Config.get_api_url('pages'),
            params={'slug': temp_slug, 'per_page': 1, 'status': 'any'},
            timeout=30
        )
        if response.status_code == 200:
            pages = response.json()
            duplicate_page = pages[0] if pages else None
        else:
            console.print("[red]Could not find created duplicate page[/red]")
            return
    
    duplicate_id = duplicate_page['id']
    console.print(f"[green]✓[/green] Duplicate created - ID: {duplicate_id}")
    console.print(f"  Slug: {temp_slug}")
    
    # Step 4: Add new formatted content
    console.print(f"\n[cyan]Step 4: Adding new formatted content...[/cyan]")

    # Publish content into the duplicate draft (canonical pipeline expects update-by-slug;
    # so we directly update by ID here with the pipeline-built payload.)
    # Easiest: temporarily set the duplicate's slug to the target slug during build is risky,
    # so we do a one-off update on this duplicate ID with the pipeline's transforms.
    # We keep this script for workflow only; monthly publishing should use publish_content_item.py.

    # Run pipeline for formatting/building (without trying to update original page)
    options = PublishOptions(status="draft", use_acf_blocks=True)
    built_id, validation = pipeline.publish_from_file(json_file, content_type="pages", options=options)
    if built_id is None:
        console.print("[red]Failed building/updating original via pipeline (page slug must exist).[/red]")
        console.print("[yellow]This workflow requires the original page slug to exist in WP.[/yellow]")
        return

    # Copy canonical content from original page into duplicate
    src = session.get(Config.get_api_url(f"pages/{built_id}"), params={"context": "edit"}, timeout=30)
    if src.status_code != 200:
        console.print("[red]Could not fetch updated original for copying.[/red]")
        return
    src_page = src.json()
    src_content = src_page.get("content", {}).get("raw", "")
    src_meta = src_page.get("meta", {})

    update_resp = session.post(
        Config.get_api_url(f"pages/{duplicate_id}"),
        json={"title": source_data.get("title", ""), "content": src_content, "status": "draft", "meta": src_meta},
        timeout=30,
    )
    if update_resp.status_code == 200:
        console.print(f"[green]✓[/green] New content added to draft duplicate")
        if not validation.ok:
            console.print("[yellow]⚠ Validation issues exist; review in WP before swapping.[/yellow]")
    else:
        console.print(f"[red]Error updating draft duplicate: {update_resp.status_code}[/red]")
        return
    
    # Step 5: Get final URLs
    response = session.get(Config.get_api_url(f'pages/{duplicate_id}'), timeout=30)
    if response.status_code == 200:
        final_page = response.json()
        draft_url = final_page.get('link', '')
    else:
        draft_url = f"https://www.camplakota.com/{temp_slug}/"
    
    # Summary
    console.print(f"\n[bold green]✅ Landing Page Processing Complete![/bold green]\n")
    
    table = Table(title="Page Status")
    table.add_column("Page", style="cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("URL", style="dim")
    
    if original_id:
        orig_response = session.get(Config.get_api_url(f'pages/{original_id}'), timeout=30)
        if orig_response.status_code == 200:
            orig = orig_response.json()
            table.add_row(
                "Original (Published)",
                str(original_id),
                orig.get('status', 'N/A'),
                orig.get('link', 'N/A')
            )
    
    table.add_row(
        "Draft (New Content)",
        str(duplicate_id),
        "draft",
        draft_url
    )
    
    console.print(table)
    
    console.print(f"\n[bold]Next Steps - How to Swap:[/bold]")
    console.print(f"\n[yellow]Option 1: Update Original with Draft Content[/yellow]")
    console.print(f"  When approved, run: Update original page (ID: {original_id}) with content from draft (ID: {duplicate_id})")
    console.print(f"  Then delete the draft duplicate")
    
    console.print(f"\n[yellow]Option 2: Swap Slugs[/yellow]")
    console.print(f"  1. Change original slug to '{target_slug}-old'")
    console.print(f"  2. Change draft slug to '{target_slug}'")
    console.print(f"  3. Publish draft, unpublish original")
    console.print(f"  4. Delete old original")
    
    console.print(f"\n[dim]Review the draft at: {draft_url}[/dim]")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'content/pages/water-sports-update.json'
    
    process_landing_page(json_file)
