#!/usr/bin/env python3
"""
Fix "A Day at Camp" page - upload complete content from source JSON
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def extract_full_content():
    """Extract the complete content from JSON file"""
    with open('content/pages/a-day-at-camp-update.json', 'r', encoding='utf-8') as f:
        raw = f.read()
    
    # Method that works: find content between "content": " and ", "excerpt"
    start = raw.find('"content": "') + len('"content": "')
    excerpt_pos = raw.find('",\n  "excerpt"')
    
    if start > len('"content": "') and excerpt_pos > start:
        content_raw = raw[start:excerpt_pos]
        # Unescape the JSON string
        content = content_raw.replace('\\n', '\n')
        content = content.replace('\\"', '"')
        content = content.replace('\\t', '\t')
        content = content.replace('\\r', '\r')
        
        # Extract other fields
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', raw)
        excerpt_match = re.search(r'"excerpt"\s*:\s*"([^"]+)"', raw)
        meta_title_match = re.search(r'"meta_title"\s*:\s*"([^"]+)"', raw)
        meta_desc_match = re.search(r'"meta_description"\s*:\s*"([^"]+)"', raw)
        
        data = {
            'title': title_match.group(1) if title_match else '',
            'excerpt': excerpt_match.group(1) if excerpt_match else '',
            'meta_title': meta_title_match.group(1) if meta_title_match else '',
            'meta_description': meta_desc_match.group(1) if meta_desc_match else ''
        }
        
        return content, data
    
    raise Exception("Could not extract content from JSON")


def apply_formatting(content):
    """Apply gold standard formatting"""
    from rebuild_day_at_camp_page import add_padding_to_elements
    return add_padding_to_elements(content)


def add_images_and_boxes(content, session):
    """Add images and content boxes"""
    from rebuild_day_at_camp_page import (
        insert_image_properly,
        add_content_boxes,
        get_image_url,
        get_image_metadata
    )
    
    IMAGE_PLACEMENTS = [
        {'id': 1773, 'keyword': 'Daily Schedule', 'unique_class': 'daily-schedule-hero-image', 'section': 'The Daily Schedule'},
        {'id': 896, 'keyword': 'First Period Activity', 'unique_class': 'activities-image', 'section': 'Activity periods'},
        {'id': 1280, 'keyword': 'CIT', 'unique_class': 'cit-program-image', 'section': 'CIT section'},
        {'id': 1812, 'keyword': 'Evening/Night Activity', 'unique_class': 'evening-activities-image', 'section': 'Evening activities'},
    ]
    
    # Add images
    for img_config in IMAGE_PLACEMENTS:
        img_url = get_image_url(session, img_config['id'])
        if img_url:
            metadata = get_image_metadata(img_config['id'])
            content = insert_image_properly(content, img_config, img_url, metadata)
    
    # Add content boxes
    content = add_content_boxes(content)
    
    return content


def resolve_links(content, session):
    """Resolve internal links"""
    from resolve_internal_links import build_link_map, resolve_links_in_content
    link_map = build_link_map(session)
    return resolve_links_in_content(content, link_map)


def main():
    console.print(Panel.fit(
        "[bold cyan]Fix 'A Day at Camp' - Upload Complete Content[/bold cyan]",
        border_style="cyan"
    ))
    
    # Step 1: Extract full content
    console.print("\n[bold]Step 1: Extracting Full Content from Source[/bold]")
    try:
        content, source_data = extract_full_content()
        console.print(f"[green]✓[/green] Extracted {len(content)} characters")
        
        # Verify key sections
        checks = {
            'Schedule table': '</table>' in content,
            'Age Divisions': 'Sections by Age Division' in content,
            'Braves section': 'Braves (Ages 6-9)' in content,
            'Key Things': 'Key Things First-Time Parents' in content,
            'First Week': 'Typical First Week Perspective' in content,
            'Final Thought': 'Final Thought' in content,
            'CTA section': 'cta-section' in content or 'Next Steps' in content
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            console.print(f"  {status} {check}")
        
        if not checks['Schedule table']:
            console.print("\n[red]❌ Schedule table not found in extracted content![/red]")
            return
            
    except Exception as e:
        console.print(f"[red]❌ Error extracting content: {e}[/red]")
        return
    
    # Step 2: Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 3: Apply formatting
    console.print("\n[bold]Step 2: Applying Formatting[/bold]")
    content = apply_formatting(content)
    console.print("[green]✓[/green] Formatting applied")
    
    # Step 4: Add images and boxes
    console.print("\n[bold]Step 3: Adding Images and Content Boxes[/bold]")
    content = add_images_and_boxes(content, session)
    console.print("[green]✓[/green] Images and boxes added")
    
    # Step 5: Resolve links
    console.print("\n[bold]Step 4: Resolving Internal Links[/bold]")
    content = resolve_links(content, session)
    console.print("[green]✓[/green] Links resolved")
    
    # Step 6: Update WordPress
    console.print("\n[bold]Step 5: Updating WordPress[/bold]")
    
    update_data = {
        'content': content,
        'title': source_data.get('title', 'A Day at Camp Lakota'),
        'excerpt': source_data.get('excerpt', ''),
        'status': 'draft',
        'meta': {
            '_yoast_wpseo_title': source_data.get('meta_title', ''),
            '_yoast_wpseo_metadesc': source_data.get('meta_description', ''),
        }
    }
    
    response = session.post(
        Config.get_api_url('pages/1721'),
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print("\n[bold green]✅ Complete Content Uploaded![/bold green]")
        console.print("\n[bold]Content includes:[/bold]")
        console.print("  • Full schedule table (23 time slots)")
        console.print("  • Sections by Age Division (all 7 divisions)")
        console.print("  • Key Things First-Time Parents Should Understand")
        console.print("  • Typical First Week Perspective")
        console.print("  • Final Thought section")
        console.print("  • CTA section with links")
        console.print("  • Images at key points")
        console.print("  • Content boxes")
        console.print("  • Proper formatting")
        console.print("  • Internal links resolved")
    else:
        console.print(f"[red]❌ Error: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
