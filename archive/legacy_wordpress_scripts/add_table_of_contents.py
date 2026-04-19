#!/usr/bin/env python3
"""
Add Table of Contents to "Everything You Need to Know" Post
Creates a clickable index with anchor links to all major sections.
"""

import re
from modules.deprecation import deprecated_script_exit
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

POST_ID = 2698

def create_slug(text: str) -> str:
    """Create URL-friendly slug from heading text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def create_table_of_contents(content: str) -> tuple:
    """Create TOC and add IDs to headings."""
    # Find all H2 headings
    h2_pattern = r'(<h2[^>]*>)(.*?)(</h2>)'
    h2_matches = list(re.finditer(h2_pattern, content))
    
    if not h2_matches:
        return content, ''
    
    # Build TOC
    toc_items = []
    updated_content = content
    offset = 0
    
    for match in reversed(h2_matches):  # Process in reverse to maintain positions
        start = match.start() + offset
        end = match.end() + offset
        opening_tag = match.group(1)
        heading_text = match.group(2)
        closing_tag = match.group(3)
        
        # Clean heading text for display
        clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
        
        # Create slug for anchor
        slug = create_slug(clean_heading)
        
        # Add ID to heading
        # Check if ID already exists
        if 'id=' not in opening_tag:
            # Add ID attribute
            if 'style=' in opening_tag:
                # Insert before style
                new_opening = opening_tag.replace('style=', f'id="{slug}" style=')
            else:
                # Add at end before closing >
                new_opening = opening_tag.rstrip('>') + f' id="{slug}">'
            
            # Replace in content
            updated_content = updated_content[:start] + new_opening + heading_text + closing_tag + updated_content[end:]
            offset += len(new_opening) - len(opening_tag)
        
        # Add to TOC
        toc_items.insert(0, {
            'text': clean_heading,
            'slug': slug
        })
    
    # Create TOC HTML
    toc_html = '<div class="table-of-contents" style="background-color: #f9f9f9; padding: 2rem; margin: 2rem 0; border-left: 4px solid #0066cc; border-radius: 8px;">\n'
    toc_html += '<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #1a3a5c; font-size: 1.5rem;">Table of Contents</h3>\n'
    toc_html += '<ul style="list-style: none; padding-left: 0; margin: 0;">\n'
    
    for item in toc_items:
        toc_html += f'  <li style="margin-bottom: 0.75rem;"><a href="#{item["slug"]}" style="color: #0066cc; text-decoration: none; font-size: 1rem; line-height: 1.6;">{item["text"]}</a></li>\n'
    
    toc_html += '</ul>\n'
    toc_html += '</div>\n'
    
    return updated_content, toc_html

def main():
    console.print(Panel.fit(
        "[bold cyan]Add Table of Contents to Blog Post[/bold cyan]",
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
    title = post.get('title', {}).get('rendered', '')
    
    console.print(f"\n[cyan]Processing: {title}[/cyan]")
    
    # Check if TOC already exists
    if 'table-of-contents' in content.lower() or 'Table of Contents' in content:
        console.print("  [yellow]⚠ Table of Contents already exists[/yellow]")
        # Still update IDs if needed
        updated_content, _ = create_table_of_contents(content)
        if updated_content != content:
            update_response = session.post(
                Config.get_api_url(f'posts/{POST_ID}'),
                json={'content': updated_content},
                timeout=30
            )
            if update_response.status_code == 200:
                console.print("  [green]✓ Updated heading IDs[/green]")
        return
    
    # Create TOC and add IDs to headings
    updated_content, toc_html = create_table_of_contents(content)
    
    if not toc_html:
        console.print("  [red]✗ No H2 headings found[/red]")
        return
    
    # Count sections
    h2_count = len(re.findall(r'<h2[^>]*>', updated_content))
    console.print(f"  [green]✓ Found {h2_count} sections[/green]")
    
    # Insert TOC after introduction (after first 2-3 paragraphs or first H2)
    # Find first H2
    first_h2 = re.search(r'<h2[^>]*>', updated_content)
    
    if first_h2:
        insert_pos = first_h2.start()
        # Check if there's intro content before first H2
        intro = updated_content[:insert_pos]
        # If intro is substantial (more than 500 chars), insert TOC before first H2
        if len(intro) > 500:
            new_content = updated_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + updated_content[insert_pos:]
        else:
            # Insert after first H2 section
            first_h2_end = re.search(r'</h2>', updated_content[insert_pos:])
            if first_h2_end:
                insert_pos = insert_pos + first_h2_end.end()
                # Find next paragraph or heading
                next_element = re.search(r'<p|<h2|<h3', updated_content[insert_pos:])
                if next_element:
                    insert_pos = insert_pos + next_element.start()
                new_content = updated_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + updated_content[insert_pos:]
            else:
                new_content = updated_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + updated_content[insert_pos:]
    else:
        # No H2 found, append TOC at beginning
        new_content = toc_html + '\n\n' + updated_content
    
    # Update post
    update_response = session.post(
        Config.get_api_url(f'posts/{POST_ID}'),
        json={'content': new_content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(f"  [green]✓ Table of Contents added[/green]")
        console.print(f"  [green]✓ Added IDs to {h2_count} headings[/green]")
        console.print(f"\n[cyan]TOC includes {h2_count} clickable sections[/cyan]")
    else:
        console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
        console.print(update_response.text[:200])

if __name__ == '__main__':
    deprecated_script_exit(
        "add_table_of_contents.py",
        "python3 publish_content_item.py /abs/path/to/content/posts/<file>.json --type posts --enable-toc",
    )
    main()
