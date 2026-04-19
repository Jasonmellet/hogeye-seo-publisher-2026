#!/usr/bin/env python3

def _publisher_bootstrap() -> None:
    import importlib.util
    from pathlib import Path
    p = Path(__file__).resolve()
    for c in p.parents:
        su = c / "scripts" / "publisher" / "site_setup.py"
        if su.is_file():
            spec = importlib.util.spec_from_file_location("_publisher_site_setup", su)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.ensure_publisher_paths()
            return
    raise RuntimeError("Could not find scripts/publisher/site_setup.py")

_publisher_bootstrap()

"""
Publish Draft Page - Simple publish when approved
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def publish_draft_page(page_id: int):
    """Publish a draft page"""
    
    console.print(Panel.fit("[bold cyan]Publish Draft Page[/bold cyan]"))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get current page
    console.print(f"\n[cyan]Getting page ID: {page_id}...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{page_id}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return
    
    page = response.json()
    current_status = page.get('status', 'N/A')
    
    console.print(f"  Current Status: {current_status}")
    console.print(f"  Title: {page.get('title', {}).get('rendered', 'N/A')}")
    
    if current_status == 'publish':
        console.print(f"[yellow]⚠[/yellow] Page is already published!")
        return
    
    # Publish it
    console.print(f"\n[cyan]Publishing page...[/cyan]")
    
    update_data = {
        'status': 'publish'
    }
    
    response = session.post(
        Config.get_api_url(f'pages/{page_id}'),
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print(f"[green]✅ Page published successfully![/green]")
        
        # Get final status
        response = session.get(Config.get_api_url(f'pages/{page_id}'), timeout=30)
        if response.status_code == 200:
            final = response.json()
            console.print(f"\n[bold]Final Status:[/bold]")
            console.print(f"  Page ID: {page_id}")
            console.print(f"  Status: {final.get('status', 'N/A')}")
            console.print(f"  URL: {final.get('link', 'N/A')}")
            console.print(f"  [green]Page is now live![/green]")
    else:
        console.print(f"[red]Error publishing: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        page_id = int(sys.argv[1])
    else:
        console.print("[red]Usage: python3 scripts/publisher/publish_draft_page.py [page_id][/red]")
        sys.exit(1)
    
    publish_draft_page(page_id)
