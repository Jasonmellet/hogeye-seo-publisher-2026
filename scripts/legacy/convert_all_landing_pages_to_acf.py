#!/usr/bin/env python3
"""
Convert All Landing Pages to ACF Block Structure
Replicates the "Our Story" page structure for all landing pages.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def html_to_acf_content_block(html_content: str, padding_top: str = "pt-4", padding_bottom: str = "pb-4") -> str:
    """Convert HTML content to ACF content block format."""
    # Escape the content for JSON - need to handle unicode properly
    escaped_content = json.dumps(html_content)[1:-1]  # Remove outer quotes
    
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

def extract_content_from_html(html_content: str) -> dict:
    """Extract structured content from HTML."""
    content = {
        'headings': [],
        'paragraphs': [],
        'lists': [],
        'images': []
    }
    
    # Extract H2 headings
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)
    content['headings'] = [h.strip() for h in h2_matches]
    
    # Extract paragraphs
    p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
    content['paragraphs'] = [re.sub(r'<[^>]+>', '', p).strip() for p in p_matches if p.strip()]
    
    # Extract lists
    ul_matches = re.findall(r'<ul[^>]*>(.*?)</ul>', html_content, re.DOTALL)
    for ul in ul_matches:
        li_items = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.DOTALL)
        content['lists'].append([re.sub(r'<[^>]+>', '', li).strip() for li in li_items])
    
    # Extract image IDs
    img_ids = re.findall(r'image[_-]?id["\s:]+(\d+)', html_content, re.IGNORECASE)
    content['images'] = [int(id) for id in img_ids]
    
    return content

def convert_page_to_acf(session, page_id: int, page_title: str, search_keywords: list) -> bool:
    """Convert a page to ACF block structure."""
    
    console.print(f"\n[cyan]Converting: {page_title} (ID: {page_id})...[/cyan]")
    
    # Get current page
    response = session.get(
        Config.get_api_url(f'pages/{page_id}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return False
    
    page = response.json()
    old_content = page.get('content', {}).get('raw', '')
    
    # Check if already using ACF blocks
    if 'wp:camplakota' in old_content:
        console.print(f"[dim]Already using ACF blocks, skipping...[/dim]")
        return True
    
    # Extract content
    extracted = extract_content_from_html(old_content)
    
    # Find relevant images
    image_ids = extracted['images']
    if not image_ids:
        # Search for images by keywords
        for keyword in search_keywords:
            img_response = session.get(
                Config.get_api_url('media'),
                params={'per_page': 10, 'search': keyword},
                timeout=30
            )
            if img_response.status_code == 200:
                media = img_response.json()
                for item in media[:3]:
                    if item['id'] not in image_ids:
                        image_ids.append(item['id'])
                if len(image_ids) >= 3:
                    break
    
    # Build ACF block structure
    blocks = []
    
    # Block 1: First heading + intro paragraph
    if extracted['headings'] and extracted['paragraphs']:
        first_section = f'<h2 class="page-title">{extracted["headings"][0]}</h2>\n{extracted["paragraphs"][0]}'
        blocks.append(html_to_acf_content_block(first_section))
    
    # Block 2: Large image (if available)
    if image_ids:
        blocks.append(create_large_image_block(image_ids[0]))
    
    # Block 3: Remaining content sections
    remaining_headings = extracted['headings'][1:] if len(extracted['headings']) > 1 else []
    remaining_paras = extracted['paragraphs'][1:] if len(extracted['paragraphs']) > 1 else []
    
    # Combine headings and paragraphs into sections
    section_idx = 0
    for i, heading in enumerate(remaining_headings):
        section_html = f'<h2>{heading}</h2>\n'
        
        # Add paragraphs after this heading
        para_start = section_idx
        para_end = para_start + 2 if para_start + 2 <= len(remaining_paras) else len(remaining_paras)
        
        for para in remaining_paras[para_start:para_end]:
            section_html += f'<p>{para}</p>\n'
        
        # Add lists if available
        if extracted['lists'] and i < len(extracted['lists']):
            section_html += '<ul>\n'
            for item in extracted['lists'][i]:
                section_html += f'<li>{item}</li>\n'
            section_html += '</ul>\n'
        
        blocks.append(html_to_acf_content_block(section_html))
        section_idx = para_end
        
        # Add two-column images after second section
        if i == 1 and len(image_ids) >= 2:
            blocks.append(create_two_column_images_block(
                image_ids[1],
                image_ids[2] if len(image_ids) > 2 else image_ids[1]
            ))
    
    # If we have leftover paragraphs, add them
    if section_idx < len(remaining_paras):
        leftover_html = '\n'.join([f'<p>{p}</p>' for p in remaining_paras[section_idx:]])
        if leftover_html:
            blocks.append(html_to_acf_content_block(leftover_html))
    
    # Join all blocks
    new_content = '\n\n'.join(blocks)
    
    # Update page
    update_response = session.post(
        Config.get_api_url(f'pages/{page_id}'),
        json={
            'content': new_content,
            'template': 'template-interior.php'
        },
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(f"[green]✓[/green] Converted {page_title} to ACF blocks")
        return True
    else:
        console.print(f"[red]✗[/red] Error updating {page_title}: {update_response.status_code}")
        return False

def main():
    console.print(Panel.fit(
        "[bold cyan]Convert All Landing Pages to ACF Blocks[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Pages to convert with their search keywords for images
    pages_to_convert = [
        (1980, 'Events & Night Activities', ['event', 'night', 'campfire', 'evening']),
        (1360, 'What to Expect', ['camp', 'expect', 'first', 'day']),
        (1721, 'A Day at Camp', ['day', 'camp', 'activity', 'schedule']),
    ]
    
    console.print(f"\n[bold]Converting {len(pages_to_convert)} landing pages...[/bold]\n")
    
    success_count = 0
    for page_id, page_title, keywords in pages_to_convert:
        if convert_page_to_acf(session, page_id, page_title, keywords):
            success_count += 1
    
    console.print(Panel.fit(
        f"[bold green]Complete![/bold green]\n\n"
        f"Converted: {success_count}/{len(pages_to_convert)} landing pages\n"
        f"All pages now use ACF blocks matching 'Our Story' structure",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
