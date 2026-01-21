#!/usr/bin/env python3
"""
Rebuild "A Day at Camp" page using gold standard approach
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Image placements for this page
IMAGE_PLACEMENTS = [
    {
        'id': 1773,  # "A Day at Camp" specific image
        'keyword': 'Daily Schedule',
        'unique_class': 'daily-schedule-hero-image',
        'section': 'The Daily Schedule'
    },
    {
        'id': 896,  # Rock climbing
        'keyword': 'First Period Activity',
        'unique_class': 'activities-image',
        'section': 'Activity periods'
    },
    {
        'id': 1280,  # CIT program
        'keyword': 'CIT',
        'unique_class': 'cit-program-image',
        'section': 'CIT section'
    },
    {
        'id': 1812,  # General camp activities
        'keyword': 'Evening/Night Activity',
        'unique_class': 'evening-activities-image',
        'section': 'Evening activities'
    },
]


def get_image_url(session, image_id: int) -> str:
    """Get the full URL for a WordPress media ID"""
    try:
        response = session.get(
            Config.get_api_url(f'media/{image_id}'),
            timeout=30
        )
        if response.status_code == 200:
            media = response.json()
            return media.get('source_url', '')
    except Exception as e:
        console.print(f"[red]Error getting image {image_id}: {e}[/red]")
    return ''


def get_image_metadata(image_id: int) -> dict:
    """Get image metadata from our metadata file"""
    try:
        metadata_path = Path("work") / "image-metadata" / "outputs" / "priority_images_metadata.json"
        if not metadata_path.exists():
            metadata_path = Path("priority_images_metadata.json")  # legacy root location
        with open(metadata_path, 'r', encoding="utf-8") as f:
            images = json.load(f)
            for img in images:
                if img.get('id') == image_id:
                    return img
    except:
        pass
    return {}


def add_padding_to_elements(content: str) -> str:
    """Add proper padding/margins to all HTML elements"""
    
    # Add padding to all paragraphs
    content = re.sub(
        r'<p>',
        r'<p style="margin-bottom: 1.5rem; line-height: 1.7;">',
        content
    )
    
    # Add padding to headings
    content = re.sub(
        r'<h2>',
        r'<h2 style="margin-top: 3rem; margin-bottom: 1.5rem; line-height: 1.3;">',
        content
    )
    
    content = re.sub(
        r'<h3>',
        r'<h3 style="margin-top: 2rem; margin-bottom: 1rem; line-height: 1.4;">',
        content
    )
    
    # First h2 shouldn't have top margin
    content = re.sub(
        r'<h2 style="margin-top: 3rem',
        r'<h2 style="margin-top: 2rem',
        content,
        count=1
    )
    
    # Style the table with proper spacing
    content = re.sub(
        r'<table class="camp-schedule"',
        r'<table class="camp-schedule" style="width:100%; border-collapse:collapse; margin:3rem 0;',
        content
    )
    
    # Ensure table has proper styling
    if 'style="width:100%' in content and 'margin:3rem 0' not in content:
        content = re.sub(
            r'(<table[^>]*style="[^"]*width:100%[^"]*")',
            r'\1 margin:3rem 0;',
            content
        )
    
    # Add padding to list items
    content = re.sub(
        r'<li>',
        r'<li style="margin-bottom: 0.5rem;">',
        content
    )
    
    return content


def insert_image_properly(content: str, image_config: dict, image_url: str, metadata: dict) -> str:
    """Insert image with consistent formatting and proper spacing"""
    
    keyword = image_config['keyword']
    unique_class = image_config['unique_class']
    
    # Find the section - look for heading or table
    # Strategy 1: Find heading containing the keyword
    pattern1 = rf'(<h[23][^>]*>[^<]*{re.escape(keyword)}[^<]*</h[23]>)'
    match = re.search(pattern1, content, re.IGNORECASE)
    
    if not match:
        # Strategy 2: Find in table cell
        pattern2 = rf'(<td[^>]*>[^<]*{re.escape(keyword)}[^<]*</td>)'
        match = re.search(pattern2, content, re.IGNORECASE)
    
    if not match:
        # Strategy 3: Find in paragraph
        pattern3 = rf'(<p[^>]*>[^<]*{re.escape(keyword)}[^<]*</p>)'
        match = re.search(pattern3, content, re.IGNORECASE)
    
    if match:
        insert_pos = match.end()
        
        # For table, insert after the table closes
        if keyword == 'Daily Schedule':
            # Find the closing </table> tag
            table_end = content.find('</table>', insert_pos)
            if table_end > 0:
                insert_pos = table_end + 8
        else:
            # Find end of next paragraph
            next_p = content.find('</p>', insert_pos)
            if next_p > 0:
                insert_pos = next_p + 4
        
        # Get metadata
        alt_text = metadata.get('alt_text', f'Camp Lakota {keyword}')
        caption = metadata.get('caption', '')
        
        # Create properly formatted image HTML
        image_html = '\n\n'
        image_html += '<div class="content-image ' + unique_class + '" style="margin: 3rem auto; max-width: 900px; text-align: center;">\n'
        image_html += f'  <img src="{image_url}" alt="{alt_text}" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: block;" />\n'
        if caption:
            image_html += f'  <p style="margin-top: 1rem; font-style: italic; color: #666; font-size: 0.95em; line-height: 1.6;">{caption}</p>\n'
        image_html += '</div>\n\n'
        
        content = content[:insert_pos] + image_html + content[insert_pos:]
        console.print(f"[green]✓[/green] Inserted {keyword} image")
        return content
    
    console.print(f"[yellow]⚠[/yellow] Could not find section for {keyword}")
    return content


def add_content_boxes(content: str) -> str:
    """Add content boxes where they add value"""
    
    # Add a "Key Takeaway" box after "Key Things First-Time Parents Should Understand"
    key_takeaway_box = '''
<div class="content-box key-takeaway-box" style="background: #e7f3ff; padding: 2.5rem; border-left: 4px solid #0066cc; margin: 3rem 0; border-radius: 4px;">
<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #0066cc;">💡 Key Takeaway for Parents</h3>
<p style="margin-bottom: 0; line-height: 1.7; font-size: 1.05em;"><strong>The schedule is full, but it's designed to be engaging, not exhausting.</strong> Every element—from rest hour to evening activities—is intentional. Your child will be busy, but they'll also be supported, rested, and having fun with friends.</p>
</div>
'''
    
    # Insert after "Key Things First-Time Parents Should Understand" heading
    key_match = re.search(r'(<h2[^>]*>[^<]*Key Things First-Time Parents[^<]*</h2>)', content, re.IGNORECASE)
    if key_match:
        insert_pos = key_match.end()
        next_p = content.find('</p>', insert_pos)
        if next_p > 0:
            insert_pos = next_p + 4
        content = content[:insert_pos] + '\n\n' + key_takeaway_box + '\n\n' + content[insert_pos:]
        console.print("[green]✓[/green] Added key takeaway box")
    
    return content


def main():
    console.print(Panel.fit("[bold cyan]Rebuild 'A Day at Camp' Page - Gold Standard[/bold cyan]"))
    
    # Load clean source content
    console.print("\n[cyan]Loading clean source content...[/cyan]")
    
    # Read as text first to handle JSON issues
    with open('content/pages/a-day-at-camp-update.json', 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Fix common JSON issues (curly quotes, etc.)
    file_content = file_content.replace('"', '"').replace('"', '"')
    file_content = file_content.replace(''', "'").replace(''', "'")
    
    try:
        source_data = json.loads(file_content)
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON Error: {e}[/red]")
        console.print("[yellow]Attempting to extract content directly...[/yellow]")
        # Fallback: extract content field manually
        import re
        content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)"', file_content, re.DOTALL)
        if content_match:
            content = content_match.group(1)
            content = content.replace('\\n', '\n').replace('\\"', '"')
            source_data = {'content': content, 'title': 'A Day at Camp Lakota'}
        else:
            raise
    
    content = source_data.get('content', source_data.get('content', ''))
    
    # Fix escaped newlines
    content = content.replace('\\n', '\n')
    
    console.print("[green]✓[/green] Loaded clean content")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 1: Add padding to all elements
    console.print("\n[bold]Step 1: Adding Proper Padding[/bold]")
    content = add_padding_to_elements(content)
    console.print("[green]✓[/green] Added padding to all paragraphs, headings, and table")
    
    # Step 2: Insert images properly
    console.print("\n[bold]Step 2: Inserting Images[/bold]")
    for image_config in IMAGE_PLACEMENTS:
        image_url = get_image_url(session, image_config['id'])
        if image_url:
            metadata = get_image_metadata(image_config['id'])
            content = insert_image_properly(content, image_config, image_url, metadata)
        else:
            console.print(f"[yellow]⚠[/yellow] Could not get URL for image {image_config['id']}")
    
    # Step 3: Add content boxes
    console.print("\n[bold]Step 3: Adding Content Boxes[/bold]")
    content = add_content_boxes(content)
    
    # Step 4: Clean up any double spacing
    content = re.sub(r'\n{4,}', '\n\n', content)
    
    # Step 5: Update page
    console.print("\n[bold]Step 4: Updating WordPress Page (ID: 1721)[/bold]")
    
    update_data = {
        'title': source_data['title'],
        'content': content,
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
        console.print("[green]✅ Page completely rebuilt with proper formatting![/green]")
        console.print("\n[bold]What was fixed:[/bold]")
        console.print("  • Started from clean source (no duplicates)")
        console.print("  • Added proper padding to ALL paragraphs (1.5rem bottom)")
        console.print("  • Added proper spacing to ALL headings (2-3rem top)")
        console.print("  • Table styled with proper margins (3rem)")
        console.print("  • Images with consistent formatting (3rem margins, max-width 900px)")
        console.print("  • Content box with proper spacing (3rem margins)")
        console.print("  • Professional, clean layout")
        console.print("  • Status: draft")
    else:
        console.print(f"[red]❌ Error: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
