#!/usr/bin/env python3
"""
Update What to Expect page with parent-facing content
"""

import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold cyan]Updating What to Expect Page[/bold cyan]\n"
        "[dim]Replacing staff content with parent-facing content[/dim]",
        border_style="cyan"
    ))
    
    # Load parent content - handle JSON parsing carefully
    try:
        with open('content/pages/what-to-expect-parent.json', 'r', encoding='utf-8') as f:
            parent_data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ JSON Error: {e}[/red]")
        console.print("[yellow]Trying to fix JSON...[/yellow]")
        # Try reading as text and fixing common issues
        with open('content/pages/what-to-expect-parent.json', 'r', encoding='utf-8') as f:
            content = f.read()
            # Replace common problematic characters
            content = content.replace('"', '"').replace('"', '"')
            content = content.replace(''', "'").replace(''', "'")
            parent_data = json.loads(content)
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Prepare update data
    update_data = {
        'title': parent_data['title'],
        'content': parent_data['content'],
        'excerpt': parent_data.get('excerpt', ''),
        'status': parent_data.get('status', 'draft'),
        'meta': {
            '_yoast_wpseo_title': parent_data.get('meta_title', ''),
            '_yoast_wpseo_metadesc': parent_data.get('meta_description', ''),
            '_yoast_wpseo_focuskw': 'what to expect at sleepaway camp',
            '_yoast_wpseo_meta-robots-noindex': '0',
            '_yoast_wpseo_meta-robots-nofollow': '0',
            '_yoast_wpseo_canonical': 'https://www.camplakota.com/what-to-expect/',
        }
    }
    
    console.print(f"\n[cyan]Updating page ID: 1360[/cyan]")
    console.print(f"[dim]New Title: {parent_data['title']}[/dim]")
    console.print(f"[dim]Content Length: {len(parent_data['content'])} characters[/dim]")
    console.print(f"[dim]Status: {parent_data.get('status', 'draft')}[/dim]")
    
    if Config.is_dry_run():
        console.print("\n[yellow]DRY RUN MODE - Would update page with parent content[/yellow]")
        console.print("\n[bold]SEO Metadata:[/bold]")
        console.print(f"  Title: {parent_data.get('meta_title', 'N/A')}")
        console.print(f"  Description: {parent_data.get('meta_description', 'N/A')[:80]}...")
        return
    
    console.print("\n[cyan]Updating page...[/cyan]")
    
    response = session.post(
        Config.get_api_url('pages/1360'),
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        console.print(f"\n[green]✅ Page updated successfully![/green]")
        console.print(f"[dim]URL: {result.get('link', 'N/A')}[/dim]")
        console.print(f"[dim]Status: {result.get('status', 'N/A')}[/dim]")
        console.print(f"[dim]Modified: {result.get('modified', 'N/A')}[/dim]")
        
        console.print("\n[bold]SEO Metadata Added:[/bold]")
        console.print(f"  Title: {parent_data.get('meta_title', 'N/A')}")
        console.print(f"  Description: {parent_data.get('meta_description', 'N/A')}")
        
        console.print("\n[yellow]⚠️  IMPORTANT:[/yellow]")
        console.print("The redirect is still active, so /what-to-expect/ redirects to staff page.")
        console.print("You should REMOVE/DISABLE the redirect in Redirection plugin now.")
        console.print("The parent content is now live on the original page.")
    else:
        console.print(f"\n[red]❌ Update failed: {response.status_code}[/red]")
        console.print(f"[dim]{response.text[:300]}[/dim]")

if __name__ == '__main__':
    main()
