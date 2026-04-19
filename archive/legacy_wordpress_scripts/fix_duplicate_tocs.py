#!/usr/bin/env python3
"""
Fix Duplicate Table of Contents
Removes all duplicate TOCs and ensures only one properly functioning TOC remains.
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
    text = re.sub(r'<[^>]+>', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text

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

def remove_all_tocs(content: str) -> str:
    """Remove all existing TOC sections."""
    # Pattern 1: Full TOC div with class
    pattern1 = r'<div[^>]*class="table-of-contents"[^>]*>.*?</div>\s*</div>'
    content = re.sub(pattern1, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Pattern 2: TOC with h3 heading
    pattern2 = r'<h3[^>]*>Table of Contents</h3>.*?</div>\s*</div>'
    content = re.sub(pattern2, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Pattern 3: Any remaining TOC-like structures
    pattern3 = r'<div[^>]*>.*?Table of Contents.*?</div>\s*</div>'
    content = re.sub(pattern3, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up any extra whitespace/newlines
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

def main():
    console.print(Panel.fit(
        "[bold yellow]Fix Duplicate Table of Contents[/bold yellow]",
        border_style="yellow"
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
    
    # Count existing TOCs
    toc_count_before = len(re.findall(r'Table of Contents', content, re.IGNORECASE))
    console.print(f"\n[cyan]Found {toc_count_before} 'Table of Contents' instances[/cyan]")
    
    # Step 1: Ensure all headings have IDs
    console.print("\n[cyan]Step 1: Ensuring all headings have IDs...[/cyan]")
    content = ensure_all_headings_have_ids(content)
    h2_count = len(re.findall(r'<h2[^>]*id="[^"]*"', content))
    console.print(f"  [green]✓ {h2_count} headings have IDs[/green]")
    
    # Step 2: Remove all existing TOCs
    console.print("\n[cyan]Step 2: Removing all duplicate TOCs...[/cyan]")
    content = remove_all_tocs(content)
    toc_count_after_removal = len(re.findall(r'Table of Contents', content, re.IGNORECASE))
    console.print(f"  [green]✓ Removed {toc_count_before - toc_count_after_removal} TOC instances[/green]")
    
    # Step 3: Create new single TOC
    console.print("\n[cyan]Step 3: Creating single, properly formatted TOC...[/cyan]")
    toc_html = create_table_of_contents(content)
    
    if not toc_html:
        console.print("  [red]✗ Could not create TOC[/red]")
        return
    
    toc_items = len(re.findall(r'<a href="#[^"]+"', toc_html))
    console.print(f"  [green]✓ TOC created with {toc_items} sections[/green]")
    
    # Step 4: Insert TOC in the right place (after introduction, before first major section)
    console.print("\n[cyan]Step 4: Inserting TOC in optimal location...[/cyan]")
    
    # Find first H2 (Introduction)
    first_h2_match = re.search(r'<h2[^>]*>', content)
    
    if first_h2_match:
        insert_pos = first_h2_match.start()
        # Check intro length
        intro = content[:insert_pos]
        
        if len(intro) > 500:
            # Insert before first H2
            new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
        else:
            # Insert after first H2 section
            first_h2_end = re.search(r'</h2>', content[insert_pos:])
            if first_h2_end:
                insert_pos = insert_pos + first_h2_end.end()
                # Find next element
                next_elem = re.search(r'<p|<h2|<h3', content[insert_pos:])
                if next_elem:
                    insert_pos = insert_pos + next_elem.start()
                new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
            else:
                new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
    else:
        new_content = toc_html + '\n\n' + content
    
    # Step 5: Update post
    console.print("\n[cyan]Step 5: Updating post...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'posts/{POST_ID}'),
        json={'content': new_content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        # Verify
        verify_response = session.get(
            Config.get_api_url(f'posts/{POST_ID}'),
            params={'context': 'edit'},
            timeout=30
        )
        if verify_response.status_code == 200:
            verify_content = verify_response.json().get('content', {}).get('raw', '')
            final_toc_count = len(re.findall(r'Table of Contents', verify_content, re.IGNORECASE))
            
            console.print(f"  [green]✓ Post updated successfully[/green]")
            console.print(f"\n[bold green]✓ Complete![/bold green]")
            console.print(f"[green]✓ Removed {toc_count_before} duplicate TOCs[/green]")
            console.print(f"[green]✓ Created 1 properly functioning TOC[/green]")
            console.print(f"[green]✓ TOC contains {toc_items} clickable sections[/green]")
            console.print(f"[green]✓ Verification: {final_toc_count} TOC instance(s) in post[/green]")
        else:
            console.print(f"  [green]✓ Post updated successfully[/green]")
    else:
        console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
        console.print(update_response.text[:200])

if __name__ == '__main__':
    deprecated_script_exit(
        "fix_duplicate_tocs.py",
        "python3 publish_content_item.py /abs/path/to/content/posts/<file>.json --type posts --enable-toc",
    )
    main()
