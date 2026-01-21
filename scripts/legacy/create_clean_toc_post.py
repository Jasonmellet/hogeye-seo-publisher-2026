#!/usr/bin/env python3
"""
Create New Clean Post with Single TOC
Fetches existing post data, removes all duplicate TOCs, and creates a new clean post.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

OLD_POST_ID = 2698

def create_slug(text: str) -> str:
    """Create URL-friendly slug from heading text."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text

def remove_all_tocs(content: str) -> str:
    """Remove ALL TOC instances from content."""
    # Remove all divs with table-of-contents class
    pattern = r'<div[^>]*class="[^"]*table-of-contents[^"]*"[^>]*>.*?</div>\s*</div>'
    content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove any remaining TOC structures
    # Find all "Table of Contents" text and remove their containing divs
    toc_positions = []
    for match in re.finditer(r'Table of Contents', content, re.IGNORECASE):
        toc_positions.append(match.start())
    
    # Remove each TOC by finding its div container
    for pos in reversed(toc_positions):
        # Look backwards for opening div
        div_start = -1
        for i in range(max(0, pos - 300), pos):
            if content[i:i+5] == '<div ':
                test_section = content[i:pos+100]
                if 'Table of Contents' in test_section or 'table-of-contents' in test_section.lower():
                    div_start = i
                    break
        
        if div_start > -1:
            # Find matching closing divs
            div_count = 0
            div_end = -1
            for k in range(div_start, min(len(content), div_start + 2500)):
                if content[k:k+5] == '<div ':
                    div_count += 1
                elif content[k:k+6] == '</div>':
                    div_count -= 1
                    if div_count == 0:
                        div_end = k + 6
                        break
            
            if div_end > div_start:
                content = content[:div_start] + content[div_end:]
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

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
        "[bold cyan]Create New Clean Post with Single TOC[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 1: Get existing post data
    console.print("\n[cyan]Step 1: Fetching existing post data...[/cyan]")
    response = session.get(
        Config.get_api_url(f'posts/{OLD_POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]✗ Error fetching post {OLD_POST_ID}[/red]")
        return
    
    post = response.json()
    console.print(f"  [green]✓ Post data retrieved[/green]")
    
    # Extract all post data
    title = post.get('title', {}).get('raw', '')
    slug = post.get('slug', '')
    status = post.get('status', 'draft')
    content = post.get('content', {}).get('raw', '')
    excerpt = post.get('excerpt', {}).get('raw', '')
    categories = post.get('categories', [])
    tags = post.get('tags', [])
    featured_media = post.get('featured_media', 0)
    
    # Get meta fields
    meta_title = None
    meta_description = None
    meta_response = session.get(
        Config.get_api_url(f'posts/{OLD_POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    if meta_response.status_code == 200:
        meta_data = meta_response.json()
        # Try to get Yoast SEO fields
        for key, value in meta_data.items():
            if key == '_yoast_wpseo_title':
                meta_title = value
            elif key == '_yoast_wpseo_metadesc':
                meta_description = value
    
    console.print(f"  [green]✓ Title: {title}[/green]")
    console.print(f"  [green]✓ Status: {status}[/green]")
    console.print(f"  [green]✓ Categories: {len(categories)}[/green]")
    console.print(f"  [green]✓ Tags: {len(tags)}[/green]")
    
    # Step 2: Clean content - remove all TOCs
    console.print("\n[cyan]Step 2: Removing all duplicate TOCs...[/cyan]")
    toc_count_before = len(re.findall(r'Table of Contents', content, re.IGNORECASE))
    console.print(f"  Found {toc_count_before} TOC instances")
    
    clean_content = remove_all_tocs(content)
    toc_count_after = len(re.findall(r'Table of Contents', clean_content, re.IGNORECASE))
    console.print(f"  [green]✓ Removed {toc_count_before - toc_count_after} TOC instances[/green]")
    
    # Step 3: Ensure all headings have IDs
    console.print("\n[cyan]Step 3: Ensuring all headings have anchor IDs...[/cyan]")
    clean_content = ensure_all_headings_have_ids(clean_content)
    h2_count = len(re.findall(r'<h2[^>]*id="[^"]*"', clean_content))
    console.print(f"  [green]✓ {h2_count} headings have IDs[/green]")
    
    # Step 4: Create single TOC
    console.print("\n[cyan]Step 4: Creating single, clean TOC...[/cyan]")
    toc_html = create_table_of_contents(clean_content)
    
    if not toc_html:
        console.print("  [red]✗ Could not create TOC[/red]")
        return
    
    toc_items = len(re.findall(r'<a href="#[^"]+"', toc_html))
    console.print(f"  [green]✓ TOC created with {toc_items} sections[/green]")
    
    # Step 5: Insert TOC in optimal location
    console.print("\n[cyan]Step 5: Inserting TOC in optimal location...[/cyan]")
    first_h2_match = re.search(r'<h2[^>]*>', clean_content)
    
    if first_h2_match:
        insert_pos = first_h2_match.start()
        intro = clean_content[:insert_pos]
        
        if len(intro) > 500:
            final_content = clean_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + clean_content[insert_pos:]
        else:
            first_h2_end = re.search(r'</h2>', clean_content[insert_pos:])
            if first_h2_end:
                insert_pos = insert_pos + first_h2_end.end()
                next_elem = re.search(r'<p|<h2|<h3', clean_content[insert_pos:])
                if next_elem:
                    insert_pos = insert_pos + next_elem.start()
                final_content = clean_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + clean_content[insert_pos:]
            else:
                final_content = clean_content[:insert_pos] + '\n\n' + toc_html + '\n\n' + clean_content[insert_pos:]
    else:
        final_content = toc_html + '\n\n' + clean_content
    
    # Step 6: Create new post
    console.print("\n[cyan]Step 6: Creating new clean post...[/cyan]")
    
    new_post_data = {
        'title': title,
        'slug': slug + '-clean',  # Add -clean to slug to avoid conflict
        'status': status,
        'content': final_content,
        'excerpt': excerpt,
        'categories': categories,
        'tags': tags,
        'featured_media': featured_media,
    }
    
    # Add meta fields if available
    if meta_title:
        new_post_data['_yoast_wpseo_title'] = meta_title
    if meta_description:
        new_post_data['_yoast_wpseo_metadesc'] = meta_description
    
    create_response = session.post(
        Config.get_api_url('posts'),
        json=new_post_data,
        timeout=30
    )
    
    if create_response.status_code == 201:
        new_post = create_response.json()
        new_post_id = new_post.get('id')
        new_post_link = new_post.get('link', '')
        
        console.print(f"  [green]✓ New post created successfully![/green]")
        console.print(f"\n[bold green]✓ Complete![/bold green]")
        console.print(f"[green]✓ New post ID: {new_post_id}[/green]")
        console.print(f"[green]✓ Slug: {new_post_data['slug']}[/green]")
        console.print(f"[green]✓ Status: {status}[/green]")
        console.print(f"[green]✓ TOC: 1 clean instance with {toc_items} sections[/green]")
        if new_post_link:
            console.print(f"[green]✓ Link: {new_post_link}[/green]")
        console.print(f"\n[cyan]You can now delete the old post (ID {OLD_POST_ID}) and update the slug if needed.[/cyan]")
    else:
        console.print(f"  [red]✗ Error creating post: {create_response.status_code}[/red]")
        console.print(create_response.text[:300])

if __name__ == '__main__':
    main()
