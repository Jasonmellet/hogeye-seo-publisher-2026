#!/usr/bin/env python3
"""
Enhance the "What to Expect" parent page with:
1. Resolved internal links
2. Inline images at key sections
3. Content boxes for visual breaks
4. Set status to draft
"""

import json
import re
from modules.auth import WordPressAuth
from modules.links import InternalLinkManager
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Image placement map: (image_id, section_keyword, position_hint)
IMAGE_PLACEMENTS = [
    (896, "rock climbing", "First, Second, and Third Periods"),
    (912, "archery", "First, Second, and Third Periods"),
    (2581, "water-sports", "First, Second, and Third Periods"),
    (899, "horseback", "First, Second, and Third Periods"),
    (1280, "Camp Moms", "The Counselors Who Support Your Child"),
    (1165, "Rookie Day", "How We Support First-Time Campers"),
]

# Content boxes to add
CONTENT_BOXES = {
    "daily_schedule": {
        "after": "Why Structure Matters",
        "html": """
<div class="content-box daily-schedule-box" style="background: #f8f9fa; padding: 2rem; border-left: 4px solid #0066cc; margin: 2rem 0;">
<h3 style="margin-top: 0; color: #0066cc;">📅 A Typical Day at Camp</h3>
<ul style="line-height: 1.8;">
<li><strong>7:00am</strong> - Reveille (Wake-up)</li>
<li><strong>9:00am</strong> - Morning Lineup</li>
<li><strong>9:35am-12:15pm</strong> - Three Activity Periods</li>
<li><strong>12:30pm-2:00pm</strong> - Lunch & Rest Hour</li>
<li><strong>2:00pm-3:15pm</strong> - Weekly Elective</li>
<li><strong>3:30pm-5:30pm</strong> - Three More Activity Periods</li>
<li><strong>5:45pm-6:30pm</strong> - Dinner</li>
<li><strong>7:15pm-9:15pm</strong> - Evening Activity</li>
<li><strong>9:15pm+</strong> - Taps (Wind-down)</li>
</ul>
</div>
"""
    },
    "safety_box": {
        "after": "We Take Safety Seriously",
        "html": """
<div class="content-box safety-box" style="background: #fff3cd; padding: 2rem; border-left: 4px solid #ffc107; margin: 2rem 0;">
<h3 style="margin-top: 0; color: #856404;">🛡️ Safety Features at Camp Lakota</h3>
<ul style="line-height: 1.8;">
<li><strong>On-Site Medical:</strong> Registered nurse + doctors on call</li>
<li><strong>Water Safety:</strong> Certified lifeguards for pool and lake</li>
<li><strong>Campus Security:</strong> Gated entrance with cameras</li>
<li><strong>Staff Training:</strong> Background checks + intensive orientation</li>
<li><strong>Emergency Preparedness:</strong> Regular drills and first responder protocols</li>
</ul>
</div>
"""
    },
    "camp_mom_box": {
        "after": "Camp Moms: Extra Support",
        "html": """
<div class="content-box camp-mom-box" style="background: #d1ecf1; padding: 2rem; border-left: 4px solid #0c5460; margin: 2rem 0;">
<h3 style="margin-top: 0; color: #0c5460;">👩‍👧 Camp Moms: Your Parent Connection</h3>
<p style="margin-bottom: 0.5rem;"><strong>For our youngest campers (Braves, ages 6-9), we have Camp Moms—actual parents who understand your concerns.</strong></p>
<ul style="line-height: 1.8; margin-bottom: 0;">
<li>Available for phone calls before camp starts</li>
<li>Parent-to-parent communication</li>
<li>Handle medication, bedtime, and emotional needs</li>
<li>Attend activities with their groups</li>
</ul>
</div>
"""
    }
}


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


def insert_image_after_section(content: str, section_keyword: str, image_id: int, image_url: str, metadata: dict) -> str:
    """Insert an image after a specific section"""
    # Try multiple strategies to find the insertion point
    
    # Strategy 1: Find heading containing the keyword
    pattern1 = rf'(<h[23]>[^<]*{re.escape(section_keyword)}[^<]*</h[23]>)'
    match = re.search(pattern1, content, re.IGNORECASE)
    
    if not match:
        # Strategy 2: Find paragraph containing the keyword
        pattern2 = rf'(<p>[^<]*{re.escape(section_keyword)}[^<]*</p>)'
        match = re.search(pattern2, content, re.IGNORECASE)
    
    if not match:
        # Strategy 3: Find any occurrence of the keyword
        pattern3 = rf'({re.escape(section_keyword)})'
        match = re.search(pattern3, content, re.IGNORECASE)
    
    if match:
        insert_pos = match.end()
        
        # Find the end of the current paragraph or heading
        next_p = content.find('</p>', insert_pos)
        next_h = content.find('</h', insert_pos)
        
        # Use the closest closing tag
        if next_p > 0 and (next_h == -1 or next_p < next_h):
            insert_pos = next_p + 4
        elif next_h > 0:
            insert_pos = next_h + 4
        
        # Get image metadata
        alt_text = metadata.get('alt_text', f'Camp Lakota {section_keyword}')
        caption = metadata.get('caption', '')
        
        # Create image HTML
        image_html = f'\n<div class="content-image" style="margin: 2rem 0; text-align: center;">\n'
        image_html += f'<img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;" />\n'
        if caption:
            image_html += f'<p style="margin-top: 0.5rem; font-style: italic; color: #666;">{caption}</p>\n'
        image_html += '</div>\n'
        
        # Insert the image
        content = content[:insert_pos] + image_html + content[insert_pos:]
        console.print(f"[green]✓[/green] Inserted image {image_id} after '{section_keyword}' section")
        return content
    
    console.print(f"[yellow]⚠[/yellow] Could not find section with keyword '{section_keyword}'")
    return content


def insert_content_box(content: str, box_key: str, box_config: dict) -> str:
    """Insert a content box after a specific heading"""
    after_text = box_config['after']
    box_html = box_config['html'].strip()
    
    # Find the heading
    pattern = rf'(<h[23]>[^<]*{re.escape(after_text)}[^<]*</h[23]>)'
    
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        insert_pos = match.end()
        # Find the end of the next paragraph
        next_p = content.find('</p>', insert_pos)
        if next_p > 0:
            insert_pos = next_p + 4
        
        content = content[:insert_pos] + '\n' + box_html + '\n' + content[insert_pos:]
        console.print(f"[green]✓[/green] Inserted {box_key} content box")
        return content
    
    console.print(f"[yellow]⚠[/yellow] Could not find heading '{after_text}' for {box_key} box")
    return content


def build_link_map(session) -> dict:
    """Build a map of slugs to URLs from WordPress"""
    link_map = {}
    
    console.print("[cyan]Building link map from WordPress...[/cyan]")
    
    # Get all pages
    try:
        response = session.get(
            Config.get_api_url('pages'),
            params={'per_page': 100, 'status': 'any'},
            timeout=30
        )
        if response.status_code == 200:
            pages = response.json()
            for page in pages:
                slug = page.get('slug', '')
                url = page.get('link', '')
                if slug and url:
                    link_map[slug] = url
                    link_map[slug.replace('-', '_')] = url  # Also support underscores
    except Exception as e:
        console.print(f"[red]Error fetching pages: {e}[/red]")
    
    # Get all posts
    try:
        response = session.get(
            Config.get_api_url('posts'),
            params={'per_page': 100, 'status': 'any'},
            timeout=30
        )
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                slug = post.get('slug', '')
                url = post.get('link', '')
                if slug and url:
                    link_map[slug] = url
                    link_map[slug.replace('-', '_')] = url
    except Exception as e:
        console.print(f"[red]Error fetching posts: {e}[/red]")
    
    console.print(f"[green]✓[/green] Built link map with {len(link_map)} entries")
    return link_map


def main():
    console.print(Panel.fit("[bold cyan]Enhancing 'What to Expect' Parent Page[/bold cyan]"))
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get the page
    console.print("\n[cyan]Fetching page from WordPress...[/cyan]")
    response = session.get(
        Config.get_api_url('pages/1360'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return
    
    page = response.json()
    content = page.get('content', {}).get('raw', '')
    
    console.print(f"[green]✓[/green] Loaded page: {page.get('title', {}).get('raw', 'N/A')}")
    
    # Step 1: Resolve internal links
    console.print("\n[bold]Step 1: Resolving Internal Links[/bold]")
    link_map = build_link_map(session)
    
    link_manager = InternalLinkManager(session)
    link_manager.slug_to_url = link_map
    
    content = link_manager.replace_link_placeholders(content)
    
    # Step 2: Insert images
    console.print("\n[bold]Step 2: Inserting Images[/bold]")
    for image_id, keyword, position in IMAGE_PLACEMENTS:
        image_url = get_image_url(session, image_id)
        if image_url:
            metadata = get_image_metadata(image_id)
            content = insert_image_after_section(content, keyword, image_id, image_url, metadata)
        else:
            console.print(f"[yellow]⚠[/yellow] Could not get URL for image {image_id}")
    
    # Step 3: Insert content boxes
    console.print("\n[bold]Step 3: Adding Content Boxes[/bold]")
    for box_key, box_config in CONTENT_BOXES.items():
        content = insert_content_box(content, box_key, box_config)
    
    # Step 4: Update the page
    console.print("\n[bold]Step 4: Updating Page in WordPress[/bold]")
    
    update_data = {
        'content': content,
        'status': 'draft'  # Set to draft
    }
    
    response = session.post(
        Config.get_api_url('pages/1360'),
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print("[green]✅ Page updated successfully![/green]")
        console.print("\n[bold]Summary:[/bold]")
        console.print("  • Internal links resolved")
        console.print("  • Images inserted at key sections")
        console.print("  • Content boxes added")
        console.print("  • Status set to draft")
    else:
        console.print(f"[red]❌ Error updating page: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
