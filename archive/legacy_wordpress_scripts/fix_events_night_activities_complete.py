#!/usr/bin/env python3
"""
Fix Events & Night Activities Page - Complete Rebuild
Rebuilds from source JSON with all H2 sections, proper formatting, and structure.
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID = 1980

def html_to_acf_content_block(html_content: str, padding_top: str = "pt-4", padding_bottom: str = "pb-4") -> str:
    """Convert HTML content to ACF content block format."""
    escaped_content = json.dumps(html_content)[1:-1]
    block = f'''<!-- wp:camplakota/content {{"name":"camplakota/content","data":{{"content":"{escaped_content}","_content":"field_6614a1b785f52","padding_top":"{padding_top}","_padding_top":"field_6614a581b0eea","padding_bottom":"{padding_bottom}","_padding_bottom":"field_6614a5d6b0eeb"}},"mode":"edit"}} /-->'''
    return block

def create_large_image_block(image_id: int, padding_top: str = "pt-4", padding_bottom: str = "pb-4", max_height: str = "500") -> str:
    """Create ACF large-image block."""
    block = f'''<!-- wp:camplakota/large-image {{"name":"camplakota/large-image","data":{{"image":{image_id},"_image":"field_6614ac8a8d6df","padding_top":"{padding_top}","_padding_top":"field_6614a6e9e8ae6","padding_bottom":"{padding_bottom}","_padding_bottom":"field_6614a6e9e8ae9","max_height":"{max_height}","_max_height":"field_661829c0ae3be"}},"mode":"edit"}} /-->'''
    return block

def create_two_column_images_block(image_id_1: int, image_id_2: int, padding_top: str = "pt-0", padding_bottom: str = "pb-0", max_height: str = "500") -> str:
    """Create ACF two-column-images block."""
    block = f'''<!-- wp:camplakota/two-column-images {{"name":"camplakota/two-column-images","data":{{"images_0_image":{image_id_1},"_images_0_image":"field_66184d55d83dd","images_1_image":{image_id_2},"_images_1_image":"field_66184d55d83dd","images":2,"_images":"field_66184d19d83dc","max_height":"{max_height}","_max_height":"field_661851eaa863b","padding_top":"{padding_top}","_padding_top":"field_6618529ec9efc","padding_bottom":"{padding_bottom}","_padding_bottom":"field_661852fbaeba5"}},"mode":"edit"}} /-->'''
    return block

def load_source_content():
    """Load content from source JSON file."""
    try:
        with open('content/pages/events-night-activities.json', 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Try reading as text
        with open('content/pages/events-night-activities.json', 'r') as f:
            file_content = f.read()
            start_idx = file_content.find('"content": "')
            if start_idx != -1:
                start_idx += len('"content": "')
                # Find matching closing quote
                end_idx = start_idx
                found_end = False
                while end_idx < len(file_content) and not found_end:
                    if file_content[end_idx] == '"':
                        if end_idx > 0 and file_content[end_idx-1] == '\\':
                            end_idx += 1
                            continue
                        look_ahead = end_idx + 1
                        while look_ahead < len(file_content) and file_content[look_ahead] in [' ', '\n', '\t']:
                            look_ahead += 1
                        if look_ahead < len(file_content) and file_content[look_ahead] in [',', '}']:
                            found_end = True
                            break
                    end_idx += 1
                
                if not found_end:
                    brace_idx = file_content.find('}', start_idx)
                    if brace_idx > start_idx:
                        last_quote = file_content.rfind('"', start_idx, brace_idx)
                        if last_quote > start_idx:
                            end_idx = last_quote
                
                content_text = file_content[start_idx:end_idx]
                content_text = content_text.replace('\\n', '\n')
                content_text = content_text.replace('\\"', '"')
                content_text = content_text.replace('\\/', '/')
                content_text = content_text.replace('&amp;', '&')
                return {'content': content_text}
    return None

def split_content_by_h2(html_content: str) -> list:
    """Split content by H2 headings, preserving each section."""
    content = html_content.replace('\\n', '\n').replace('\\"', '"').replace('\\/', '/')
    
    # Find all H2 sections
    h2_pattern = r'(<h2[^>]*>.*?</h2>)'
    h2_matches = list(re.finditer(h2_pattern, content, re.DOTALL))
    
    if not h2_matches:
        return [content]
    
    result = []
    
    # First section: everything before first H2
    if h2_matches[0].start() > 0:
        result.append(content[:h2_matches[0].start()].strip())
    
    # Process each H2 section
    for i, match in enumerate(h2_matches):
        section_start = match.start()
        if i + 1 < len(h2_matches):
            section_end = h2_matches[i + 1].start()
        else:
            section_end = len(content)
        
        section = content[section_start:section_end].strip()
        if section:
            result.append(section)
    
    return result

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix Events & Night Activities Page - Complete Rebuild[/bold cyan]",
        border_style="cyan"
    ))
    
    # Load source content
    console.print("\n[cyan]Loading source content from JSON...[/cyan]")
    source_data = load_source_content()
    
    if not source_data:
        console.print("[red]Error loading source JSON[/red]")
        return
    
    source_content = source_data.get('content', '')
    console.print(f"[green]✓[/green] Loaded source content ({len(source_content)} characters)\n")
    
    # Split into sections
    console.print("[cyan]Splitting content into H2 sections...[/cyan]")
    sections = split_content_by_h2(source_content)
    console.print(f"[green]✓[/green] Found {len(sections)} sections\n")
    
    # Show sections
    for i, section in enumerate(sections, 1):
        h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', section)
        if h2_match:
            heading_text = re.sub(r'<[^>]+>', '', h2_match.group(1)).strip()
            console.print(f"  Section {i}: {heading_text[:60]}...")
        else:
            console.print(f"  Section {i}: (intro)")
    
    # Build ACF blocks
    console.print("\n[cyan]Building ACF blocks...[/cyan]")
    blocks = []
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Block 1: Intro with first H2
    if sections:
        blocks.append(html_to_acf_content_block(sections[0]))
    
    # Block 2: Large image
    img_response = session.get(
        Config.get_api_url('media'),
        params={'per_page': 10, 'search': 'event'},
        timeout=30
    )
    image_id = 1959  # Default (the featured image)
    if img_response.status_code == 200:
        media = img_response.json()
        if media:
            image_id = media[0]['id']
    
    blocks.append(create_large_image_block(image_id))
    
    # Block 3+: Remaining sections
    for i, section in enumerate(sections[1:], 1):
        blocks.append(html_to_acf_content_block(section))
        
        # Add two-column images after second major section
        if i == 1:  # After first H2 section
            img_ids = [image_id]
            if len(media) > 1:
                img_ids.append(media[1]['id'])
            if len(media) > 2:
                img_ids.append(media[2]['id'])
            else:
                img_ids.append(image_id)
            
            if len(img_ids) >= 2:
                blocks.append(create_two_column_images_block(img_ids[1], img_ids[2] if len(img_ids) > 2 else img_ids[1]))
    
    # Join all blocks
    new_content = '\n\n'.join(blocks)
    
    console.print(f"[green]✓[/green] Created {len(blocks)} ACF blocks\n")
    
    # Update page
    console.print("[cyan]Updating page in WordPress...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        json={
            'content': new_content,
            'template': 'template-interior.php'
        },
        timeout=30
    )
    
    if update_response.status_code == 200:
        # Verify H2 count
        h2_count = 0
        for block in new_content.split('<!-- wp:camplakota/content'):
            json_match = re.search(r'\{.*?"content":"(.*?)".*?\}', block, re.DOTALL)
            if json_match:
                try:
                    decoded = json.loads('"' + json_match.group(1) + '"')
                    h2_count += len(re.findall(r'<h2[^>]*>', decoded))
                except:
                    pass
        
        console.print(Panel.fit(
            f"[bold green]✓ Fixed![/bold green]\n\n"
            f"Rebuilt Events & Night Activities page with:\n"
            f"  • {len(blocks)} ACF blocks\n"
            f"  • {h2_count} H2 headings\n"
            f"  • All sections from source JSON\n"
            f"  • Images at natural break points",
            border_style="green"
        ))
    else:
        console.print(f"[red]Error updating page: {update_response.status_code}[/red]")
        console.print(update_response.text)

if __name__ == '__main__':
    main()
