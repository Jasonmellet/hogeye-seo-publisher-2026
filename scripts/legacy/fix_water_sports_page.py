#!/usr/bin/env python3
"""
Fix Water Sports Landing Page
Fixes issues: missing border-radius on images, duplicate CTA, proper spacing.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID = 806
PAGE_TITLE = "Water Sports"

def fix_image_border_radius(content: str) -> str:
    """Add border-radius: 8px to all images that don't have it."""
    
    def add_border_radius(match):
        img_tag = match.group(0)
        
        # Skip if already has border-radius
        if 'border-radius' in img_tag:
            return img_tag
        
        # Check if has style attribute
        if 'style=' in img_tag:
            # Add border-radius to existing style
            img_tag = re.sub(
                r'style="([^"]*)"',
                r'style="\1; border-radius: 8px;"',
                img_tag
            )
        else:
            # Add new style attribute
            img_tag = img_tag.replace('<img', '<img style="border-radius: 8px;"')
        
        return img_tag
    
    content = re.sub(r'<img[^>]*>', add_border_radius, content)
    return content

def remove_duplicate_cta(content: str) -> str:
    """Remove duplicate CTA sections, keeping only the last one."""
    
    # Find all CTA sections
    cta_pattern = r'(<div class="cta-section"[^>]*>.*?</div>\s*</div>)'
    matches = list(re.finditer(cta_pattern, content, re.DOTALL | re.IGNORECASE))
    
    if len(matches) > 1:
        console.print(f"[yellow]Found {len(matches)} CTA sections, removing duplicates...[/yellow]")
        
        # Keep only the last one
        for i, match in enumerate(matches[:-1]):  # All except the last
            content = content[:match.start()] + content[match.end():]
            # Adjust subsequent match positions
            for j in range(i + 1, len(matches)):
                matches[j] = re.search(cta_pattern, content, re.DOTALL | re.IGNORECASE)
        
        console.print(f"[green]✓[/green] Removed {len(matches) - 1} duplicate CTA section(s)")
    
    return content

def fix_hero_overlay_positioning(content: str) -> str:
    """Ensure hero overlay is positioned bottom-right."""
    
    # Check if hero overlay exists
    if 'hero-overlay' not in content:
        return content
    
    # Fix positioning if it's not bottom-right
    if 'position: absolute; bottom: 20px; right: 20px' not in content:
        # Replace any incorrect positioning
        content = re.sub(
            r'(<div class="hero-overlay"[^>]*style="[^"]*position:[^"]*")',
            r'<div class="hero-overlay" style="position: absolute; bottom: 20px; right: 20px; background: #1a3a5c; color: white; padding: 1rem 2rem; font-size: 1.5rem; font-weight: bold; border-radius: 4px;"',
            content
        )
        console.print("[green]✓[/green] Fixed hero overlay positioning")
    
    return content

def ensure_proper_spacing(content: str) -> str:
    """Ensure all paragraphs and headings have proper spacing."""
    
    # Add spacing to paragraphs without it
    def add_para_spacing(match):
        tag = match.group(0)
        if 'style=' in tag:
            if 'margin-bottom: 1.5rem' not in tag:
                tag = re.sub(r'style="([^"]*)"', r'style="\1; margin-bottom: 1.5rem; line-height: 1.7;"', tag)
        else:
            tag = tag.replace('<p>', '<p style="margin-bottom: 1.5rem; line-height: 1.7;">')
        return tag
    
    content = re.sub(r'<p[^>]*>', add_para_spacing, content)
    
    # Add spacing to H2 headings
    def add_h2_spacing(match):
        tag = match.group(0)
        if 'style=' in tag:
            if 'margin-top: 3rem' not in tag:
                tag = re.sub(r'style="([^"]*)"', r'style="\1; margin-top: 3rem; margin-bottom: 1.5rem;"', tag)
        else:
            tag = tag.replace('<h2>', '<h2 style="margin-top: 3rem; margin-bottom: 1.5rem;">')
        return tag
    
    content = re.sub(r'<h2[^>]*>', add_h2_spacing, content)
    
    return content

def main():
    console.print(Panel.fit(
        f"[bold cyan]Fix {PAGE_TITLE} Landing Page[/bold cyan]",
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
    
    # Fix issues
    console.print("[cyan]Fixing image border-radius...[/cyan]")
    content = fix_image_border_radius(content)
    
    console.print("[cyan]Removing duplicate CTA sections...[/cyan]")
    content = remove_duplicate_cta(content)
    
    console.print("[cyan]Fixing hero overlay positioning...[/cyan]")
    content = fix_hero_overlay_positioning(content)
    
    console.print("[cyan]Ensuring proper spacing...[/cyan]")
    content = ensure_proper_spacing(content)
    
    # Update page
    console.print(f"\n[cyan]Updating page in WordPress...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(Panel.fit(
            f"[bold green]✓ Fixed![/bold green]\n\n"
            f"Fixed {PAGE_TITLE} page:\n"
            f"  • Added border-radius: 8px to all images\n"
            f"  • Removed duplicate CTA sections\n"
            f"  • Fixed hero overlay positioning\n"
            f"  • Ensured proper spacing",
            border_style="green"
        ))
    else:
        console.print(f"[red]Error updating page: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
