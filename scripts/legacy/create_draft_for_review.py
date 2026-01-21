#!/usr/bin/env python3
"""
Create a draft duplicate of a page for review
Keeps the published page intact while allowing review of new content
"""

import sys
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def create_draft_duplicate(page_id: int, temp_slug_suffix: str = '-draft-review'):
    """Create a draft duplicate of an existing page"""
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get the existing page
    console.print(f"[cyan]Fetching page ID: {page_id}...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{page_id}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return None
    
    original_page = response.json()
    
    # Create new page with temp slug
    original_slug = original_page.get('slug', '')
    temp_slug = original_slug + temp_slug_suffix
    
    console.print(f"[cyan]Creating draft duplicate with slug: {temp_slug}...[/cyan]")
    
    new_page_data = {
        'title': original_page.get('title', {}).get('raw', '') + ' (Draft Review)',
        'slug': temp_slug,
        'content': original_page.get('content', {}).get('raw', ''),
        'excerpt': original_page.get('excerpt', {}).get('raw', ''),
        'status': 'draft',
        'meta': original_page.get('meta', {})
    }
    
    response = session.post(
        Config.get_api_url('pages'),
        json=new_page_data,
        timeout=30
    )
    
    if response.status_code == 201:
        new_page = response.json()
        new_id = new_page['id']
        new_url = new_page.get('link', '')
        
        console.print(f"[green]✅ Draft duplicate created![/green]")
        console.print(f"\n[bold]Details:[/bold]")
        console.print(f"  New Page ID: {new_id}")
        console.print(f"  Slug: {temp_slug}")
        console.print(f"  URL: {new_url}")
        console.print(f"  Status: draft")
        console.print(f"\n[yellow]Original page (ID: {page_id}) remains unchanged[/yellow]")
        console.print(f"[dim]Review the draft, then we can update the original when approved[/dim]")
        
        return new_id
    else:
        console.print(f"[red]Error creating draft: {response.status_code}[/red]")
        console.print(response.text[:500])
        return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        page_id = int(sys.argv[1])
    else:
        # Default to water-sports page
        page_id = 806
    
    console.print(Panel.fit(f"[bold cyan]Create Draft Duplicate for Review[/bold cyan]"))
    console.print(f"\n[bold]Page ID:[/bold] {page_id}")
    
    create_draft_duplicate(page_id)
