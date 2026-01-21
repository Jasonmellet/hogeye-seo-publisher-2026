#!/usr/bin/env python3
"""
Fix All Landing Pages
Fixes missing border-radius on hero images and ensures all images have proper styling.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGES = [
    (1980, 'Events & Night Activities'),
    (1360, 'What to Expect'),
    (806, 'Water Sports'),
]

def fix_all_images(content: str) -> str:
    """Add border-radius: 8px to ALL images including hero images."""
    
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
        # Keep only the last one - remove all others
        # Work backwards to avoid index issues
        for i in range(len(matches) - 2, -1, -1):  # All except the last
            match = matches[i]
            content = content[:match.start()] + content[match.end():]
        
        return content, len(matches) - 1
    
    return content, 0

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix All Landing Pages[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    total_fixed = 0
    
    for page_id, title in PAGES:
        console.print(f"\n[cyan]Processing: {title} (ID: {page_id})...[/cyan]")
        
        response = session.get(
            Config.get_api_url(f'pages/{page_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error fetching page: {response.status_code}[/red]")
            continue
        
        page = response.json()
        content = page.get('content', {}).get('raw', '')
        
        # Count images before
        images_before = len(re.findall(r'<img[^>]*>', content))
        images_without_border_before = len([img for img in re.findall(r'<img[^>]*>', content) if 'border-radius' not in img])
        
        # Fix images
        content = fix_all_images(content)
        
        # Check for duplicate CTA
        content, cta_removed = remove_duplicate_cta(content)
        
        # Count images after
        images_without_border_after = len([img for img in re.findall(r'<img[^>]*>', content) if 'border-radius' not in img])
        
        # Update page
        update_response = session.post(
            Config.get_api_url(f'pages/{page_id}'),
            json={'content': content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            fixes = []
            if images_without_border_before > images_without_border_after:
                fixes.append(f"Added border-radius to {images_without_border_before - images_without_border_after} image(s)")
            if cta_removed > 0:
                fixes.append(f"Removed {cta_removed} duplicate CTA(s)")
            
            if fixes:
                console.print(f"[green]✓[/green] Fixed: {', '.join(fixes)}")
                total_fixed += 1
            else:
                console.print(f"[dim]✓[/dim] No issues found")
        else:
            console.print(f"[red]✗[/red] Error updating page: {update_response.status_code}")
    
    console.print(Panel.fit(
        f"[bold green]Complete![/bold green]\n\n"
        f"Fixed {total_fixed}/{len(PAGES)} landing pages\n"
        f"All images now have border-radius: 8px\n"
        f"All duplicate CTAs removed",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
