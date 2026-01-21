#!/usr/bin/env python3
"""
Update What to Expect Landing Page
Adds hero section according to landing page design template.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID = 1360
PAGE_TITLE = "What to Expect"

def add_hero_section(content: str, hero_image_url: str = '') -> str:
    """Add hero section with overlay banner at the beginning of content."""
    
    # Check if hero already exists
    if 'hero-section' in content.lower() or 'hero-overlay' in content.lower():
        console.print("[dim]Hero section already exists, skipping...[/dim]")
        return content
    
    # Default hero image if none provided
    if not hero_image_url:
        hero_image_url = 'https://www.camplakota.com/wp-content/uploads/2024/01/what-to-expect-hero.jpg'
    
    hero_html = f'''<div class="hero-section" style="position: relative; margin-bottom: 3rem;">
  <img src="{hero_image_url}" alt="What to Expect at Camp Lakota" style="width: 100%; height: auto; display: block; max-height: 500px; object-fit: cover; border-radius: 8px;">
  <div class="hero-overlay" style="position: absolute; bottom: 20px; right: 20px; background: #1a3a5c; color: white; padding: 1rem 2rem; font-size: 1.5rem; font-weight: bold; border-radius: 4px;">
    What to Expect
  </div>
</div>

'''
    
    return hero_html + content

def main():
    console.print(Panel.fit(
        f"[bold cyan]Update {PAGE_TITLE} Landing Page[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get current page
    console.print(f"\n[cyan]Fetching page {PAGE_ID}...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return
    
    page = response.json()
    content = page.get('content', {}).get('raw', '')
    
    console.print(f"[green]✓[/green] Page loaded ({len(content)} characters)\n")
    
    # Update content
    console.print("[cyan]Adding hero section...[/cyan]")
    content = add_hero_section(content)
    
    # Update page
    console.print(f"\n[cyan]Updating page in WordPress...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(Panel.fit(
            f"[bold green]✓ Success![/bold green]\n\n"
            f"Updated {PAGE_TITLE} page with:\n"
            f"  • Hero section with overlay banner",
            border_style="green"
        ))
    else:
        console.print(f"[red]Error updating page: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
