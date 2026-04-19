#!/usr/bin/env python3
"""
Restore original published page and create draft duplicate for review
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
import json
import re

console = Console()

def restore_and_create_draft(page_id: int, json_file: str, draft_slug: str):
    """Restore original page and create draft duplicate"""
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    console.print(Panel.fit(f"[bold cyan]Restore & Create Draft for Review[/bold cyan]"))
    
    # Step 1: Get current draft content (our new content)
    console.print("\n[cyan]Step 1: Getting new draft content...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{page_id}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return
    
    draft_page = response.json()
    new_content = draft_page.get('content', {}).get('raw', '')
    console.print(f"[green]✓[/green] Got new content ({len(new_content)} chars)")
    
    # Step 2: Load original content from JSON file
    console.print("\n[cyan]Step 2: Loading original content from source...[/cyan]")
    with open(json_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Fix JSON issues
    file_content = file_content.replace('"', '"').replace('"', '"')
    file_content = file_content.replace(''', "'").replace(''', "'")
    
    try:
        source_data = json.loads(file_content)
        original_content = source_data.get('content', '').replace('\\n', '\n')
    except:
        content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)"', file_content, re.DOTALL)
        original_content = content_match.group(1).replace('\\n', '\n').replace('\\"', '"') if content_match else ''
    
    console.print(f"[green]✓[/green] Got original content ({len(original_content)} chars)")
    
    # Step 3: Restore original page to published
    console.print("\n[cyan]Step 3: Restoring original page to published...[/cyan]")
    restore_data = {
        'content': original_content,
        'status': 'publish'
    }
    
    response = session.post(
        Config.get_api_url(f'pages/{page_id}'),
        json=restore_data,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print("[green]✓[/green] Original page restored to published")
    else:
        console.print(f"[red]Error: {response.status_code}[/red]")
        return
    
    # Step 4: Create draft duplicate with new content
    console.print("\n[cyan]Step 4: Creating draft duplicate...[/cyan]")
    
    new_page_data = {
        'title': draft_page.get('title', {}).get('raw', '') + ' (Draft Review)',
        'slug': draft_slug,
        'content': new_content,
        'excerpt': draft_page.get('excerpt', {}).get('raw', ''),
        'status': 'draft',
        'meta': draft_page.get('meta', {})
    }
    
    response = session.post(
        Config.get_api_url('pages'),
        json=new_page_data,
        timeout=30
    )
    
    console.print(f"[dim]Response status: {response.status_code}[/dim]")
    console.print(f"[dim]Response text (first 200 chars): {response.text[:200]}[/dim]")
    
    if response.status_code == 201:
        try:
            new_page = response.json()
            console.print(f"[green]✅ Draft duplicate created![/green]")
            console.print(f"\n[bold]Review URLs:[/bold]")
            console.print(f"  Published (original): https://www.camplakota.com/activities/water-sports/")
            console.print(f"  Draft (new content): {new_page.get('link', 'N/A')}")
            console.print(f"\n[yellow]Review the draft, then we'll update the published page when approved[/yellow]")
        except Exception as e:
            console.print(f"[red]Error parsing response: {e}[/red]")
            console.print(f"[yellow]But page may have been created - check WordPress admin[/yellow]")
    else:
        console.print(f"[red]Error creating draft: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    restore_and_create_draft(
        page_id=806,
        json_file='content/pages/water-sports-update.json',
        draft_slug='water-sports-draft-review'
    )
