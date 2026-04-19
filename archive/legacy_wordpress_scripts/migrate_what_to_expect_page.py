#!/usr/bin/env python3
"""
Migrate What to Expect Page
Moves existing staff-facing content to new URL before replacing with parent content
"""

import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Config
from modules.auth import WordPressAuth

console = Console()


def find_page_by_slug(session, slug):
    """Find existing page by slug"""
    response = session.get(
        Config.get_api_url('pages'),
        params={'slug': slug, 'per_page': 1},
        timeout=30
    )
    
    if response.status_code == 200:
        pages = response.json()
        if pages:
            return pages[0]
    return None


def get_page_content(session, page_id):
    """Get full page content"""
    response = session.get(
        Config.get_api_url(f'pages/{page_id}'),
        params={'context': 'edit'},  # Get editable content
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()
    return None


def create_new_page(session, page_data):
    """Create a new page"""
    response = session.post(
        Config.get_api_url('pages'),
        json=page_data,
        timeout=30
    )
    
    return response


def main():
    console.print(Panel.fit(
        "[bold cyan]What to Expect Page Migration[/bold cyan]\n"
        "[dim]Step 1: Move staff content to new URL[/dim]",
        border_style="cyan"
    ))
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 1: Find existing staff page
    console.print("\n[cyan]Step 1: Finding existing staff page...[/cyan]")
    existing_page = find_page_by_slug(session, 'what-to-expect')
    
    if not existing_page:
        console.print("[red]❌ No page found with slug 'what-to-expect'[/red]")
        return
    
    page_id = existing_page['id']
    current_title = existing_page.get('title', {}).get('rendered', 'Unknown')
    current_url = existing_page.get('link', 'N/A')
    
    console.print(f"[green]✓ Found page:[/green] {current_title} (ID: {page_id})")
    console.print(f"[dim]Current URL: {current_url}[/dim]")
    
    # Step 2: Get full page content
    console.print("\n[cyan]Step 2: Retrieving full page content...[/cyan]")
    full_page = get_page_content(session, page_id)
    
    if not full_page:
        console.print("[red]❌ Could not retrieve page content[/red]")
        return
    
    # Extract content
    staff_content = full_page.get('content', {}).get('raw', '')
    staff_excerpt = full_page.get('excerpt', {}).get('raw', '')
    staff_title = full_page.get('title', {}).get('raw', current_title)
    
    console.print(f"[green]✓ Retrieved content ({len(staff_content)} chars)[/green]")
    
    # Step 3: Check if new location already exists
    console.print("\n[cyan]Step 3: Checking if new location exists...[/cyan]")
    new_page = find_page_by_slug(session, 'work-at-lakota/what-to-expect')
    
    if new_page:
        console.print("[yellow]⚠️  Page already exists at /work-at-lakota/what-to-expect/[/yellow]")
        console.print(f"[dim]ID: {new_page['id']}, URL: {new_page.get('link', 'N/A')}[/dim]")
        response = console.input("\n[cyan]Continue anyway? (y/n): [/cyan]")
        if response.lower() != 'y':
            return
    else:
        # Step 4: Create new page at new location
        console.print("\n[cyan]Step 4: Creating new page at /work-at-lakota/what-to-expect/[/cyan]")
        
        if Config.is_dry_run():
            console.print("\n[yellow]DRY RUN MODE - Would create page:[/yellow]")
            console.print(f"  Title: {staff_title}")
            console.print(f"  Slug: work-at-lakota/what-to-expect")
            console.print(f"  Content: {len(staff_content)} characters")
            console.print("\n[yellow]⚠️  After creating, you'll need to:[/yellow]")
            console.print("  1. Set up 301 redirect: /what-to-expect/ → /work-at-lakota/what-to-expect/")
            console.print("  2. Update navigation menus")
            console.print("  3. Then update original page with parent content")
            return
        
        # Prepare new page data
        new_page_data = {
            'title': staff_title,
            'content': staff_content,
            'excerpt': staff_excerpt,
            'status': 'publish',
            'slug': 'work-at-lakota/what-to-expect',
            'parent': 0  # Check if work-at-lakota parent page exists
        }
        
        # Try to find parent page
        parent_page = find_page_by_slug(session, 'work-at-lakota')
        if parent_page:
            new_page_data['parent'] = parent_page['id']
            console.print(f"[green]✓ Found parent page 'Work at Lakota' (ID: {parent_page['id']})[/green]")
        else:
            console.print("[yellow]⚠️  Parent page 'work-at-lakota' not found. Creating as top-level page.[/yellow]")
        
        # Create the page
        response = create_new_page(session, new_page_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            new_page_id = result.get('id', 'unknown')
            new_page_url = result.get('link', 'N/A')
            
            console.print(f"\n[green]✅ New staff page created![/green]")
            console.print(f"[dim]ID: {new_page_id}[/dim]")
            console.print(f"[dim]URL: {new_page_url}[/dim]")
            
            # Summary table
            table = Table(title="Migration Status")
            table.add_column("Step", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("URL", style="dim")
            
            table.add_row("1. Create new staff page", "✅ Complete", new_page_url)
            table.add_row("2. Set up 301 redirect", "⏸️  Manual", "/what-to-expect/ → /work-at-lakota/what-to-expect/")
            table.add_row("3. Update original page", "⏸️  Pending", "/what-to-expect/ (parent content)")
            
            console.print("\n")
            console.print(table)
            
            console.print("\n[yellow]⚠️  NEXT STEPS (Manual):[/yellow]")
            console.print("1. Set up 301 redirect in WordPress (Redirection plugin or .htaccess)")
            console.print("2. Update navigation menus to point to new staff page URL")
            console.print("3. Test redirect works correctly")
            console.print("4. Then run update_page.py to replace /what-to-expect/ with parent content")
            
        else:
            console.print(f"\n[red]❌ Failed to create page: {response.status_code}[/red]")
            console.print(f"[dim]{response.text[:300]}[/dim]")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
