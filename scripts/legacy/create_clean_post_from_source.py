#!/usr/bin/env python3
"""
Create Clean Post from Source JSON
Reads from source JSON file and creates a new post with clean TOC.
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

SOURCE_FILE = 'content/posts/everything-you-need-to-know-sleepaway-camp-guide.json'

def create_slug(text: str) -> str:
    """Create URL-friendly slug from heading text."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text

def ensure_all_headings_have_ids(content: str) -> str:
    """Ensure all H2 headings have anchor IDs."""
    updated = content
    
    h2_pattern = r'(<h2)([^>]*>)(.*?)(</h2>)'
    
    def add_id(match):
        opening = match.group(1)
        attrs = match.group(2)
        text = match.group(3)
        closing = match.group(4)
        
        if 'id=' in attrs:
            return match.group(0)
        
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        slug = create_slug(clean_text)
        
        if attrs.strip() == '>':
            new_attrs = f' id="{slug}">'
        else:
            new_attrs = attrs.rstrip('>') + f' id="{slug}">'
        
        return opening + new_attrs + text + closing
    
    updated = re.sub(h2_pattern, add_id, updated)
    return updated

def create_table_of_contents(content: str) -> str:
    """Create a single, properly formatted table of contents."""
    # Find all H2 headings with IDs
    h2_pattern = r'<h2[^>]*id="([^"]*)"[^>]*>(.*?)</h2>'
    h2_matches = list(re.finditer(h2_pattern, content))
    
    if not h2_matches:
        return ''
    
    # Build TOC items (exclude FAQ and duplicates)
    toc_items = []
    seen_ids = set()
    
    for match in h2_matches:
        heading_id = match.group(1)
        heading_text = match.group(2)
        clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
        
        # Skip FAQ in TOC
        if 'frequently asked questions' in clean_heading.lower():
            continue
        
        # Skip duplicates
        if heading_id in seen_ids:
            continue
        seen_ids.add(heading_id)
        
        toc_items.append({
            'id': heading_id,
            'text': clean_heading
        })
    
    if not toc_items:
        return ''
    
    # Create TOC HTML
    toc_html = '''<div class="table-of-contents" style="background-color: #f9f9f9; padding: 2rem; margin: 2rem 0; border-left: 4px solid #0066cc; border-radius: 8px;">
<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #1a3a5c; font-size: 1.5rem; font-weight: bold;">Table of Contents</h3>
<ul style="list-style: none; padding-left: 0; margin: 0;">
'''
    
    for item in toc_items:
        toc_html += f'''  <li style="margin-bottom: 0.75rem;">
    <a href="#{item['id']}" style="color: #0066cc; text-decoration: none; font-size: 1rem; line-height: 1.6; transition: color 0.2s;">
      {item['text']}
    </a>
  </li>
'''
    
    toc_html += '''</ul>
</div>
'''
    
    return toc_html

def main():
    console.print(Panel.fit(
        "[bold cyan]Create Clean Post from Source JSON[/bold cyan]",
        border_style="cyan"
    ))
    
    # Step 1: Read source JSON
    console.print("\n[cyan]Step 1: Reading source JSON file...[/cyan]")
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            post_data = json.load(f)
        console.print(f"  [green]✓ File loaded[/green]")
    except Exception as e:
        console.print(f"  [red]✗ Error reading file: {e}[/red]")
        return
    
    title = post_data.get('title', '')
    slug = post_data.get('slug', '')
    content = post_data.get('content', '')
    
    console.print(f"  [green]✓ Title: {title}[/green]")
    console.print(f"  [green]✓ Slug: {slug}[/green]")
    console.print(f"  [green]✓ Content length: {len(content):,} characters[/green]")
    
    # Step 2: Ensure headings have IDs
    console.print("\n[cyan]Step 2: Ensuring all headings have anchor IDs...[/cyan]")
    content = ensure_all_headings_have_ids(content)
    h2_count = len(re.findall(r'<h2[^>]*id="[^"]*"', content))
    console.print(f"  [green]✓ {h2_count} headings have IDs[/green]")
    
    # Step 3: Create TOC
    console.print("\n[cyan]Step 3: Creating table of contents...[/cyan]")
    toc_html = create_table_of_contents(content)
    
    if not toc_html:
        console.print("  [red]✗ Could not create TOC[/red]")
        return
    
    toc_items = len(re.findall(r'<a href="#[^"]+"', toc_html))
    console.print(f"  [green]✓ TOC created with {toc_items} sections[/green]")
    
    # Step 4: Insert TOC
    console.print("\n[cyan]Step 4: Inserting TOC in optimal location...[/cyan]")
    first_h2_match = re.search(r'<h2[^>]*>', content)
    
    if first_h2_match:
        insert_pos = first_h2_match.start()
        intro = content[:insert_pos]
        
        if len(intro) > 500:
            final_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
        else:
            first_h2_end = re.search(r'</h2>', content[insert_pos:])
            if first_h2_end:
                insert_pos = insert_pos + first_h2_end.end()
                next_elem = re.search(r'<p|<h2|<h3', content[insert_pos:])
                if next_elem:
                    insert_pos = insert_pos + next_elem.start()
                final_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
            else:
                final_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
    else:
        final_content = toc_html + '\n\n' + content
    
    # Step 5: Create post
    console.print("\n[cyan]Step 5: Creating new post...[/cyan]")
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get category and tag IDs from existing post
    console.print("\n[cyan]Step 5a: Getting category and tag IDs from existing post...[/cyan]")
    old_post_response = session.get(
        Config.get_api_url(f'posts/2698'),
        params={'context': 'edit'},
        timeout=30
    )
    
    categories = []
    tags = []
    featured_media = 0
    
    if old_post_response.status_code == 200:
        old_post = old_post_response.json()
        categories = old_post.get('categories', [])
        tags = old_post.get('tags', [])
        featured_media = old_post.get('featured_media', 0)
        console.print(f"  [green]✓ Categories: {categories}[/green]")
        console.print(f"  [green]✓ Tags: {tags}[/green]")
        console.print(f"  [green]✓ Featured Media: {featured_media}[/green]")
    
    new_post_data = {
        'title': title,
        'slug': slug,
        'status': post_data.get('status', 'draft'),
        'content': final_content,
        'excerpt': post_data.get('excerpt', ''),
        'categories': categories,
        'tags': tags,
        'featured_media': featured_media,
    }
    
    # Add meta fields
    if 'meta_title' in post_data:
        new_post_data['_yoast_wpseo_title'] = post_data['meta_title']
    if 'meta_description' in post_data:
        new_post_data['_yoast_wpseo_metadesc'] = post_data['meta_description']
    
    create_response = session.post(
        Config.get_api_url('posts'),
        json=new_post_data,
        timeout=30
    )
    
    if create_response.status_code == 201:
        try:
            new_post = create_response.json()
            new_post_id = new_post.get('id')
            new_post_link = new_post.get('link', '')
            
            console.print(f"  [green]✓ New post created successfully![/green]")
            console.print(f"\n[bold green]✓ Complete![/bold green]")
            console.print(f"[green]✓ New post ID: {new_post_id}[/green]")
            console.print(f"[green]✓ Slug: {slug}[/green]")
            console.print(f"[green]✓ Status: {new_post_data['status']}[/green]")
            console.print(f"[green]✓ TOC: 1 clean instance with {toc_items} sections[/green]")
            if new_post_link:
                console.print(f"[green]✓ Link: {new_post_link}[/green]")
        except Exception as e:
            console.print(f"  [yellow]⚠ Response received but couldn't parse JSON: {e}[/yellow]")
            console.print(f"  [cyan]Response text: {create_response.text[:500]}[/cyan]")
    else:
        console.print(f"  [red]✗ Error creating post: {create_response.status_code}[/red]")
        console.print(f"  [red]Response: {create_response.text[:500]}[/red]")

if __name__ == '__main__':
    main()
