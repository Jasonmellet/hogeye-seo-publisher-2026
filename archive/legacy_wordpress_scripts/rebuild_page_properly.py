#!/usr/bin/env python3
"""
Complete page rebuild - start from clean source and add everything properly
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Image placements with proper metadata
IMAGE_PLACEMENTS = [
    {
        'id': 896,
        'keyword': 'rock climbing',
        'unique_class': 'rock-climbing-image',
        'section': 'First, Second, and Third Periods'
    },
    {
        'id': 912,
        'keyword': 'archery',
        'unique_class': 'archery-image',
        'section': 'First, Second, and Third Periods'
    },
    {
        'id': 2581,
        'keyword': 'water-sports',
        'unique_class': 'watersports-image',
        'section': 'First, Second, and Third Periods'
    },
    {
        'id': 899,
        'keyword': 'horseback',
        'unique_class': 'horseback-image',
        'section': 'First, Second, and Third Periods'
    },
    {
        'id': 1280,
        'keyword': 'Camp Moms',
        'unique_class': 'camp-moms-image',
        'section': 'Camp Moms: Extra Support'
    },
    {
        'id': 1165,
        'keyword': 'Rookie Day',
        'unique_class': 'rookie-day-image',
        'section': 'Rookie Day'
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
    
    return content


def insert_image_properly(content: str, image_config: dict, image_url: str, metadata: dict) -> str:
    """Insert image with consistent formatting and proper spacing"""
    
    keyword = image_config['keyword']
    unique_class = image_config['unique_class']
    
    # Find the section - look for the heading first
    section_pattern = rf'(<h3>[^<]*{re.escape(keyword)}[^<]*</h3>)'
    match = re.search(section_pattern, content, re.IGNORECASE)
    
    if not match:
        # Try finding in paragraph
        para_pattern = rf'(<p[^>]*>[^<]*{re.escape(keyword)}[^<]*</p>)'
        match = re.search(para_pattern, content, re.IGNORECASE)
    
    if match:
        insert_pos = match.end()
        
        # Find end of next paragraph for insertion point
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
    """Add content boxes only where they add value"""
    
    # Safety box after "We Take Safety Seriously"
    safety_box = '''
<div class="content-box safety-features-box" style="background: #fff3cd; padding: 2.5rem; border-left: 4px solid #ffc107; margin: 3rem 0; border-radius: 4px;">
<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #856404;">🛡️ Safety Features at Camp Lakota</h3>
<ul style="line-height: 1.8; margin-bottom: 0; padding-left: 1.5rem;">
<li style="margin-bottom: 0.75rem;"><strong>On-Site Medical:</strong> Registered nurse + doctors on call</li>
<li style="margin-bottom: 0.75rem;"><strong>Water Safety:</strong> Certified lifeguards for pool and lake</li>
<li style="margin-bottom: 0.75rem;"><strong>Campus Security:</strong> Gated entrance with cameras</li>
<li style="margin-bottom: 0.75rem;"><strong>Staff Training:</strong> Background checks + intensive orientation</li>
<li style="margin-bottom: 0;"><strong>Emergency Preparedness:</strong> Regular drills and first responder protocols</li>
</ul>
</div>
'''
    
    # Camp Mom box after "Camp Moms: Extra Support"
    camp_mom_box = '''
<div class="content-box camp-mom-feature-box" style="background: #d1ecf1; padding: 2.5rem; border-left: 4px solid #0c5460; margin: 3rem 0; border-radius: 4px;">
<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: #0c5460;">👩‍👧 Camp Moms: Your Parent Connection</h3>
<p style="margin-bottom: 1rem; line-height: 1.7;"><strong>For our youngest campers (Braves, ages 6-9), we have Camp Moms—actual parents who understand your concerns.</strong></p>
<ul style="line-height: 1.8; margin-bottom: 0; padding-left: 1.5rem;">
<li style="margin-bottom: 0.75rem;">Available for phone calls before camp starts</li>
<li style="margin-bottom: 0.75rem;">Parent-to-parent communication</li>
<li style="margin-bottom: 0.75rem;">Handle medication, bedtime, and emotional needs</li>
<li style="margin-bottom: 0;">Attend activities with their groups</li>
</ul>
</div>
'''
    
    # Insert safety box - find "We Take Safety Seriously" heading (full text may vary)
    safety_match = re.search(r'(<h3[^>]*>[^<]*We Take Safety Seriously[^<]*</h3>)', content, re.IGNORECASE)
    if safety_match:
        insert_pos = safety_match.end()
        # Find end of next paragraph
        next_p = content.find('</p>', insert_pos)
        if next_p > 0:
            insert_pos = next_p + 4
        content = content[:insert_pos] + '\n\n' + safety_box + '\n\n' + content[insert_pos:]
        console.print("[green]✓[/green] Added safety features box")
    else:
        console.print("[yellow]⚠[/yellow] Could not find 'We Take Safety Seriously' heading")
    
    # Insert camp mom box - find "Camp Moms: Extra Support" heading
    camp_mom_match = re.search(r'(<h3[^>]*>[^<]*Camp Moms: Extra Support[^<]*</h3>)', content, re.IGNORECASE)
    if camp_mom_match:
        insert_pos = camp_mom_match.end()
        # Find end of next paragraph
        next_p = content.find('</p>', insert_pos)
        if next_p > 0:
            insert_pos = next_p + 4
        content = content[:insert_pos] + '\n\n' + camp_mom_box + '\n\n' + content[insert_pos:]
        console.print("[green]✓[/green] Added camp mom box")
    else:
        console.print("[yellow]⚠[/yellow] Could not find 'Camp Moms: Extra Support' heading")
    
    return content


def main():
    console.print(Panel.fit("[bold red]COMPLETE PAGE REBUILD[/bold red]"))
    
    # Load clean source content
    console.print("\n[cyan]Loading clean source content...[/cyan]")
    with open('content/pages/what-to-expect-parent.json', 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    content = source_data['content']
    
    # Fix escaped newlines
    content = content.replace('\\n', '\n')
    
    console.print("[green]✓[/green] Loaded clean content")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Step 1: Add padding to all elements
    console.print("\n[bold]Step 1: Adding Proper Padding[/bold]")
    content = add_padding_to_elements(content)
    console.print("[green]✓[/green] Added padding to all paragraphs and headings")
    
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
    console.print("\n[bold]Step 4: Updating WordPress Page[/bold]")
    
    update_data = {
        'content': content,
        'status': 'draft'
    }
    
    response = session.post(
        Config.get_api_url('pages/1360'),
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        console.print("[green]✅ Page completely rebuilt with proper formatting![/green]")
        console.print("\n[bold]What was fixed:[/bold]")
        console.print("  • Started from clean source (no duplicates)")
        console.print("  • Added proper padding to ALL paragraphs (1.5rem bottom)")
        console.print("  • Added proper spacing to ALL headings (2-3rem top)")
        console.print("  • Images with consistent formatting (3rem margins)")
        console.print("  • Content boxes with proper spacing (3rem margins)")
        console.print("  • No duplicate sections")
    else:
        console.print(f"[red]❌ Error: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
