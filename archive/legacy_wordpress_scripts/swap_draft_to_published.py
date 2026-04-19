#!/usr/bin/env python3
"""
Swap Draft to Published - Update original page with draft content
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def swap_draft_to_published(original_id: int, draft_id: int, delete_draft: bool = True):
    """Update original published page with draft content"""
    
    console.print(Panel.fit("[bold cyan]Swap Draft to Published[/bold cyan]"))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get draft content
    console.print(f"\n[cyan]Step 1: Getting draft content (ID: {draft_id})...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{draft_id}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching draft: {response.status_code}[/red]")
        return False
    
    draft_page = response.json()
    
    # Get all content from draft
    draft_content = {
        'title': draft_page.get('title', {}).get('raw', ''),
        'content': draft_page.get('content', {}).get('raw', ''),
        'excerpt': draft_page.get('excerpt', {}).get('raw', ''),
        'meta': draft_page.get('meta', {}),
        'status': 'publish'  # Publish the original
    }
    
    console.print(f"[green]✓[/green] Got draft content")
    
    # Update original page
    console.print(f"\n[cyan]Step 2: Updating original page (ID: {original_id})...[/cyan]")
    
    response = session.post(
        Config.get_api_url(f'pages/{original_id}'),
        json=draft_content,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print(f"[green]✓[/green] Original page updated with new content")
    else:
        console.print(f"[red]Error updating original: {response.status_code}[/red]")
        console.print(response.text[:500])
        return False
    
    # Delete draft if requested
    if delete_draft:
        console.print(f"\n[cyan]Step 3: Deleting draft duplicate (ID: {draft_id})...[/cyan]")
        
        response = session.delete(
            Config.get_api_url(f'pages/{draft_id}'),
            params={'force': True},
            timeout=30
        )
        
        if response.status_code == 200:
            console.print(f"[green]✓[/green] Draft duplicate deleted")
        else:
            console.print(f"[yellow]⚠[/yellow] Could not delete draft (may need manual deletion)")
    
    # Get final status
    response = session.get(Config.get_api_url(f'pages/{original_id}'), timeout=30)
    if response.status_code == 200:
        final = response.json()
        console.print(f"\n[bold green]✅ Swap Complete![/bold green]")
        console.print(f"\n[bold]Final Status:[/bold]")
        console.print(f"  Page ID: {original_id}")
        console.print(f"  Status: {final.get('status', 'N/A')}")
        console.print(f"  URL: {final.get('link', 'N/A')}")
        console.print(f"  Title: {final.get('title', {}).get('rendered', 'N/A')}")
    
    return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) >= 3:
        original_id = int(sys.argv[1])
        draft_id = int(sys.argv[2])
        delete_draft = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
    else:
        # Default to water-sports
        original_id = 806
        draft_id = 2711
        delete_draft = True
    
    swap_draft_to_published(original_id, draft_id, delete_draft)
