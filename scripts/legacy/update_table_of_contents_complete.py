#!/usr/bin/env python3
"""
Update Table of Contents to Include All Major Sections
Rebuilds TOC to include all H2 headings (excluding FAQ which is already a section).
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

POST_ID = 2698

def create_slug(text: str) -> str:
    """Create URL-friendly slug from heading text."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text

def rebuild_table_of_contents(content: str) -> str:
    """Rebuild TOC to include all H2 headings."""
    # Find all H2 headings with IDs
    h2_pattern = r'<h2[^>]*id="([^"]*)"[^>]*>(.*?)</h2>'
    h2_matches = list(re.finditer(h2_pattern, content))
    
    if not h2_matches:
        return content
    
    # Build TOC items (exclude FAQ section as it's already a major section)
    toc_items = []
    for match in h2_matches:
        heading_id = match.group(1)
        heading_text = match.group(2)
        clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
        
        # Skip FAQ section in TOC (it's already a section)
        if 'frequently asked questions' in clean_heading.lower():
            continue
        
        toc_items.append({
            'id': heading_id,
            'text': clean_heading
        })
    
    # Create new TOC HTML
    toc_html = '<div class="table-of-contents" style="background-color: #f9f9f9; padding: 2rem; margin: 2rem 0; border-left: 4px solid #0066cc; border-radius: 8px;">\n'
    toc_html += '<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #1a3a5c; font-size: 1.5rem;">Table of Contents</h3>\n'
    toc_html += '<ul style="list-style: none; padding-left: 0; margin: 0;">\n'
    
    for item in toc_items:
        toc_html += f'  <li style="margin-bottom: 0.75rem;"><a href="#{item["id"]}" style="color: #0066cc; text-decoration: none; font-size: 1rem; line-height: 1.6;">{item["text"]}</a></li>\n'
    
    toc_html += '</ul>\n'
    toc_html += '</div>\n'
    
    # Replace existing TOC
    toc_pattern = r'<div[^>]*class="table-of-contents"[^>]*>.*?</div>\s*</div>'
    if re.search(toc_pattern, content, re.DOTALL):
        content = re.sub(toc_pattern, toc_html, content, flags=re.DOTALL)
    else:
        # TOC not found, insert after first H2
        first_h2 = re.search(r'<h2[^>]*>', content)
        if first_h2:
            insert_pos = first_h2.start()
            content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
    
    return content

def main():
    console.print(Panel.fit(
        "[bold cyan]Update Table of Contents - Complete[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get post
    response = session.get(
        Config.get_api_url(f'posts/{POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]✗ Error fetching post {POST_ID}[/red]")
        return
    
    post = response.json()
    content = post.get('content', {}).get('raw', '')
    
    # Count headings
    h2_count = len(re.findall(r'<h2[^>]*id="[^"]*"', content))
    console.print(f"\n[cyan]Found {h2_count} H2 headings with IDs[/cyan]")
    
    # Rebuild TOC
    updated_content = rebuild_table_of_contents(content)
    
    # Count TOC links
    toc_links = len(re.findall(r'<a href="#[^"]+"[^>]*>', updated_content))
    
    if updated_content != content:
        # Update post
        update_response = session.post(
            Config.get_api_url(f'posts/{POST_ID}'),
            json={'content': updated_content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            console.print(f"[green]✓ Table of Contents updated[/green]")
            console.print(f"[green]✓ TOC now includes {toc_links} clickable sections[/green]")
        else:
            console.print(f"[red]✗ Error updating: {update_response.status_code}[/red]")
    else:
        console.print(f"[green]✓ TOC already includes all sections[/green]")

if __name__ == '__main__':
    main()
