#!/usr/bin/env python3
"""
Final TOC Fix - Remove ALL TOC-related divs and create one clean TOC
"""

import re
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

def remove_all_toc_divs(content: str) -> str:
    """Remove ALL divs containing 'table-of-contents'."""
    # Find all divs with table-of-contents class
    pattern = r'<div[^>]*class="[^"]*table-of-contents[^"]*"[^>]*>.*?</div>\s*</div>'
    content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove any div that contains "Table of Contents" text
    # Find all positions
    toc_positions = []
    for match in re.finditer(r'Table of Contents', content, re.IGNORECASE):
        toc_positions.append(match.start())
    
    # Remove each one by finding its containing div
    for pos in reversed(toc_positions):
        # Look backwards for opening div
        start = pos
        div_start = -1
        for i in range(max(0, pos - 300), pos):
            if content[i:i+5] == '<div ':
                # Check if this div contains our TOC text
                test_section = content[i:pos+100]
                if 'Table of Contents' in test_section or 'table-of-contents' in test_section.lower():
                    div_start = i
                    break
        
        if div_start > -1:
            # Find matching closing divs
            div_count = 0
            end = div_start
            i = div_start
            while i < len(content) and i < div_start + 2500:
                if content[i:i+5] == '<div ':
                    div_count += 1
                elif content[i:i+6] == '</div>':
                    div_count -= 1
                    if div_count == 0:
                        end = i + 6
                        break
                i += 1
            
            if end > div_start:
                content = content[:div_start] + content[end:]
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

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
        "[bold cyan]Final TOC Cleanup[/bold cyan]",
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
    
    # Count before
    toc_text_before = len(re.findall(r'Table of Contents', content, re.IGNORECASE))
    toc_div_before = len(re.findall(r'table-of-contents', content, re.IGNORECASE))
    console.print(f"\n[cyan]Before:[/cyan] {toc_text_before} TOC text, {toc_div_before} TOC divs")
    
    # Step 1: Ensure headings have IDs
    console.print("\n[cyan]Step 1: Ensuring headings have IDs...[/cyan]")
    content = ensure_all_headings_have_ids(content)
    h2_count = len(re.findall(r'<h2[^>]*id="[^"]*"', content))
    console.print(f"  [green]✓ {h2_count} headings have IDs[/green]")
    
    # Step 2: Remove ALL TOC divs
    console.print("\n[cyan]Step 2: Removing ALL TOC divs...[/cyan]")
    content = remove_all_toc_divs(content)
    
    toc_text_after = len(re.findall(r'Table of Contents', content, re.IGNORECASE))
    toc_div_after = len(re.findall(r'table-of-contents', content, re.IGNORECASE))
    console.print(f"  [green]✓ After: {toc_text_after} TOC text, {toc_div_after} TOC divs[/green]")
    
    # Step 3: Create new TOC
    console.print("\n[cyan]Step 3: Creating new TOC...[/cyan]")
    toc_html = create_table_of_contents(content)
    
    if not toc_html:
        console.print("  [red]✗ Could not create TOC[/red]")
        return
    
    toc_items = len(re.findall(r'<a href="#[^"]+"', toc_html))
    console.print(f"  [green]✓ TOC with {toc_items} sections[/green]")
    
    # Step 4: Insert TOC
    console.print("\n[cyan]Step 4: Inserting TOC...[/cyan]")
    first_h2_match = re.search(r'<h2[^>]*>', content)
    
    if first_h2_match:
        insert_pos = first_h2_match.start()
        intro = content[:insert_pos]
        
        if len(intro) > 500:
            new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
        else:
            first_h2_end = re.search(r'</h2>', content[insert_pos:])
            if first_h2_end:
                insert_pos = insert_pos + first_h2_end.end()
                next_elem = re.search(r'<p|<h2|<h3', content[insert_pos:])
                if next_elem:
                    insert_pos = insert_pos + next_elem.start()
                new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
            else:
                new_content = content[:insert_pos] + '\n\n' + toc_html + '\n\n' + content[insert_pos:]
    else:
        new_content = toc_html + '\n\n' + content
    
    # Step 5: Update
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
            final_toc_text = len(re.findall(r'Table of Contents', verify_content, re.IGNORECASE))
            final_toc_div = len(re.findall(r'table-of-contents', verify_content, re.IGNORECASE))
            
            console.print(f"  [green]✓ Post updated[/green]")
            console.print(f"\n[bold green]✓ Complete![/bold green]")
            console.print(f"[green]✓ Final: {final_toc_text} TOC text, {final_toc_div} TOC divs[/green]")
            console.print(f"[green]✓ TOC contains {toc_items} clickable sections[/green]")
            
            if final_toc_text == 1 and final_toc_div == 1:
                console.print(f"\n[bold green]✓ Perfect! Only 1 TOC remains[/bold green]")
            else:
                console.print(f"\n[yellow]⚠ May need additional cleanup[/yellow]")
        else:
            console.print(f"  [green]✓ Post updated[/green]")
    else:
        console.print(f"  [red]✗ Error: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
