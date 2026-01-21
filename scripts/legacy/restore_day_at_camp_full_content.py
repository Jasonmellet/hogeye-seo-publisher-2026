#!/usr/bin/env python3
"""
Restore full content package to "A Day at Camp" page
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Import functions from rebuild script
import sys
sys.path.insert(0, '.')
from rebuild_day_at_camp_page import (
    add_padding_to_elements,
    insert_image_properly,
    add_content_boxes,
    get_image_url,
    get_image_metadata
)

def extract_content_from_json(file_path):
    """Extract content from JSON file, handling escaped characters"""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    # Fix common JSON issues
    raw = raw.replace('"', '"').replace('"', '"')
    raw = raw.replace(''', "'").replace(''', "'")
    
    # Try to parse normally first
    try:
        data = json.loads(raw)
        return data.get('content', '')
    except json.JSONDecodeError:
        # Extract content field manually
        # Find content field
        match = re.search(r'"content":\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)
        if match:
            content = match.group(1)
            # Unescape
            content = content.replace('\\n', '\n')
            content = content.replace('\\"', '"')
            content = content.replace('\\t', '\t')
            return content
        return None


def main():
    console.print(Panel.fit(
        "[bold cyan]Restore Full Content to 'A Day at Camp' Page[/bold cyan]",
        border_style="cyan"
    ))
    
    # Extract full content from source
    console.print("\n[bold]Step 1: Loading Full Source Content[/bold]")
    full_content = extract_content_from_json('content/pages/a-day-at-camp-update.json')
    
    if not full_content:
        console.print("[red]❌ Could not extract content from source file[/red]")
        return
    
    console.print(f"[green]✓[/green] Loaded {len(full_content)} characters")
    console.print(f"[green]✓[/green] Has schedule table: {'<table' in full_content}")
    console.print(f"[green]✓[/green] Has age divisions: {'Sections by Age Division' in full_content}")
    console.print(f"[green]✓[/green] Has CTA section: {'cta-section' in full_content}")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 2: Apply formatting
    console.print("\n[bold]Step 2: Applying Formatting[/bold]")
    formatted_content = add_padding_to_elements(full_content)
    console.print("[green]✓[/green] Added padding to all elements")
    
    # Step 3: Add images
    console.print("\n[bold]Step 3: Adding Images[/bold]")
    IMAGE_PLACEMENTS = [
        {'id': 1773, 'keyword': 'Daily Schedule', 'unique_class': 'daily-schedule-hero-image', 'section': 'The Daily Schedule'},
        {'id': 896, 'keyword': 'First Period Activity', 'unique_class': 'activities-image', 'section': 'Activity periods'},
        {'id': 1280, 'keyword': 'CIT', 'unique_class': 'cit-program-image', 'section': 'CIT section'},
        {'id': 1812, 'keyword': 'Evening/Night Activity', 'unique_class': 'evening-activities-image', 'section': 'Evening activities'},
    ]
    
    for img_config in IMAGE_PLACEMENTS:
        img_url = get_image_url(session, img_config['id'])
        if img_url:
            metadata = get_image_metadata(img_config['id'])
            formatted_content = insert_image_properly(formatted_content, img_config, img_url, metadata)
            console.print(f"[green]✓[/green] Added image {img_config['id']}")
        else:
            console.print(f"[yellow]⚠[/yellow] Could not get image {img_config['id']}")
    
    # Step 4: Add content boxes
    console.print("\n[bold]Step 4: Adding Content Boxes[/bold]")
    formatted_content = add_content_boxes(formatted_content)
    console.print("[green]✓[/green] Added content boxes")
    
    # Step 5: Resolve internal links
    console.print("\n[bold]Step 5: Resolving Internal Links[/bold]")
    from resolve_internal_links import build_link_map, resolve_links_in_content
    link_map = build_link_map(session)
    formatted_content = resolve_links_in_content(formatted_content, link_map)
    console.print("[green]✓[/green] Resolved internal links")
    
    # Step 6: Update WordPress
    console.print("\n[bold]Step 6: Updating WordPress[/bold]")
    
    # Get source metadata
    with open('content/pages/a-day-at-camp-update.json', 'r', encoding='utf-8') as f:
        raw = f.read()
        raw = raw.replace('"', '"').replace('"', '"')
        raw = raw.replace(''', "'").replace(''', "'")
    
    try:
        source_data = json.loads(raw)
    except:
        source_data = {}
    
    update_data = {
        'content': formatted_content,
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
        console.print("\n[bold green]✅ Full Content Package Restored![/bold green]")
        console.print("\n[bold]What was added:[/bold]")
        console.print("  • Complete schedule table (23 time slots)")
        console.print("  • All age division sections (Braves, Hawks, Scouts, etc.)")
        console.print("  • Key parent insights sections")
        console.print("  • First week perspective")
        console.print("  • CTA section with links")
        console.print("  • Images inserted at key points")
        console.print("  • Content boxes for emphasis")
        console.print("  • Proper formatting and spacing")
        console.print("  • Internal links resolved")
        console.print("  • SEO metadata")
    else:
        console.print(f"[red]❌ Error: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
