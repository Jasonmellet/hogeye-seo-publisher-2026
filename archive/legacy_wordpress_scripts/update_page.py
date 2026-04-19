#!/usr/bin/env python3
"""
Update existing WordPress page script
Updates content for existing pages instead of creating new ones
"""

import json
from rich.console import Console
from rich.panel import Panel

from config import Config
from modules.auth import WordPressAuth

console = Console()


def find_page_by_slug(session, slug):
    """Find existing page by slug"""
    response = session.get(
        Config.get_api_url('pages'),
        params={'slug': slug, 'status': 'publish'},
        timeout=30
    )
    
    if response.status_code == 200:
        pages = response.json()
        if pages:
            return pages[0]  # Return first match
    return None


def update_page(session, page_id, page_data):
    """Update existing page"""
    response = session.post(
        Config.get_api_url(f'pages/{page_id}'),
        json=page_data,
        timeout=30
    )
    
    return response


def main():
    console.print(Panel.fit(
        "[bold cyan]Update Existing WordPress Page[/bold cyan]\n"
        "[dim]Updating water-sports page with new content[/dim]",
        border_style="cyan"
    ))
    
    # Load the update JSON
    with open('content/pages/water-sports-update.json', 'r') as f:
        update_data = json.load(f)
    
    slug = update_data['slug']
    
    console.print(f"\n[cyan]Looking for existing page with slug:[/cyan] {slug}")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Find existing page
    existing_page = find_page_by_slug(session, slug)
    
    if not existing_page:
        console.print(f"[red]❌ Page not found with slug: {slug}[/red]")
        return
    
    page_id = existing_page['id']
    current_title = existing_page.get('title', {}).get('rendered', 'Unknown')
    
    console.print(f"[green]✓ Found page:[/green] {current_title} (ID: {page_id})")
    console.print(f"[dim]URL: {existing_page['link']}[/dim]")
    
    # Confirm update
    if Config.is_dry_run():
        console.print("\n[yellow]DRY RUN MODE - Would update page with:[/yellow]")
        console.print(f"  New Title: {update_data['title']}")
        console.print(f"  New Meta Title: {update_data.get('meta_title', 'N/A')}")
        console.print(f"  Content Length: {len(update_data['content'])} characters")
        return
    
    console.print(f"\n[cyan]Updating page...[/cyan]")
    
    # Prepare update data
    page_update = {
        'title': update_data['title'],
        'content': update_data['content'],
        'excerpt': update_data.get('excerpt', ''),
        'status': update_data.get('status', 'publish')
    }
    
    # Update the page
    response = update_page(session, page_id, page_update)
    
    if response.status_code == 200:
        result = response.json()
        console.print(f"\n[green]✅ Page updated successfully![/green]")
        console.print(f"[dim]URL: {result['link']}[/dim]")
        console.print(f"[dim]Modified: {result.get('modified', 'N/A')}[/dim]")
    else:
        console.print(f"\n[red]❌ Update failed: {response.status_code}[/red]")
        console.print(f"[dim]{response.text[:200]}[/dim]")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
