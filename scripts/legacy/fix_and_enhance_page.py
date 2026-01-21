#!/usr/bin/env python3
"""
Improved page enhancement script that:
1. Checks for existing elements before inserting (idempotent)
2. Removes duplicates
3. Uses better placement logic
4. Adds proper spacing
5. Avoids redundant information
"""

import json
import re
from modules.auth import WordPressAuth
from modules.links import InternalLinkManager
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Image placement map: (image_id, section_keyword, unique_class)
IMAGE_PLACEMENTS = [
    (896, "rock climbing", "rock-climbing-image"),
    (912, "archery", "archery-image"),
    (2581, "water-sports", "watersports-image"),
    (899, "horseback", "horseback-image"),
    (1280, "Camp Moms", "camp-moms-image"),
    (1165, "Rookie Day", "rookie-day-image"),
]

# Content boxes - improved placement to avoid redundancy
CONTENT_BOXES = {
    "safety_box": {
        "after": "We Take Safety Seriously",
        "unique_class": "safety-features-box",
        "html": """
<div class="content-box safety-features-box" style="background: #fff3cd; padding: 2rem; border-left: 4px solid #ffc107; margin: 2.5rem 0; border-radius: 4px;">
<h3 style="margin-top: 0; color: #856404;">🛡️ Safety Features at Camp Lakota</h3>
<ul style="line-height: 1.8; margin-bottom: 0;">
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
        "unique_class": "camp-mom-feature-box",
        "html": """
<div class="content-box camp-mom-feature-box" style="background: #d1ecf1; padding: 2rem; border-left: 4px solid #0c5460; margin: 2.5rem 0; border-radius: 4px;">
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


def remove_duplicates(content: str) -> str:
    """Remove duplicate content boxes and images"""
    console.print("[cyan]Checking for duplicates...[/cyan]")
    
    removed_count = 0
    
    # Remove duplicate content boxes - keep first, remove rest
    for box_key, box_config in CONTENT_BOXES.items():
        unique_class = box_config['unique_class']
        # Match the entire div including nested content
        pattern = rf'(<div[^>]*class="[^"]*{re.escape(unique_class)}[^"]*"[^>]*>.*?</div>\s*)'
        matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
        
        if len(matches) > 1:
            console.print(f"[yellow]Found {len(matches)} instances of {box_key}, keeping first...[/yellow]")
            # Keep first, remove rest (process in reverse to maintain positions)
            for match in reversed(matches[1:]):
                content = content[:match.start()] + content[match.end():]
                removed_count += 1
    
    # Remove old images without unique classes (from previous script runs)
    # Find all content-image divs
    old_image_pattern = r'<div[^>]*class="[^"]*content-image[^"]*"[^>]*>.*?</div>\s*'
    old_images = list(re.finditer(old_image_pattern, content, re.DOTALL | re.IGNORECASE))
    
    # Remove old images that don't have unique classes
    for match in reversed(old_images):
        match_content = content[match.start():match.end()]
        # Check if it has any unique class
        has_unique = any(unique_class in match_content for _, _, unique_class in IMAGE_PLACEMENTS)
        if not has_unique:
            console.print(f"[yellow]Removing old image without unique class...[/yellow]")
            content = content[:match.start()] + content[match.end():]
            removed_count += 1
    
    # Remove duplicate images with unique classes - keep first occurrence
    for image_id, keyword, unique_class in IMAGE_PLACEMENTS:
        pattern = rf'(<div[^>]*class="[^"]*{re.escape(unique_class)}[^"]*"[^>]*>.*?</div>\s*)'
        matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
        
        if len(matches) > 1:
            console.print(f"[yellow]Found {len(matches)} instances of {unique_class} image, keeping first...[/yellow]")
            for match in reversed(matches[1:]):
                content = content[:match.start()] + content[match.end():]
                removed_count += 1
    
    # Remove old daily schedule box (redundant - we don't want this box)
    old_pattern = r'<div[^>]*class="[^"]*daily-schedule-box[^"]*"[^>]*>.*?</div>\s*'
    old_matches = len(re.findall(old_pattern, content, re.DOTALL | re.IGNORECASE))
    if old_matches > 0:
        content = re.sub(old_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        console.print(f"[green]✓[/green] Removed {old_matches} redundant daily schedule box(es)")
        removed_count += old_matches
    
    # Remove any orphaned content-image divs without unique classes (old format)
    # This is a safety measure
    orphaned = re.findall(r'<div[^>]*class="[^"]*content-image[^"]*"[^>]*>(?!.*?(?:rock-climbing|archery|watersports|horseback|camp-moms|rookie-day))', content, re.DOTALL)
    if orphaned:
        console.print(f"[yellow]Found {len(orphaned)} orphaned image divs, cleaning...[/yellow]")
    
    if removed_count > 0:
        console.print(f"[green]✓[/green] Removed {removed_count} duplicate element(s)")
    else:
        console.print("[green]✓[/green] No duplicates found")
    
    return content


def insert_image_after_section(content: str, section_keyword: str, image_id: int, image_url: str, metadata: dict, unique_class: str) -> str:
    """Insert an image after a specific section (only if not already present)"""
    
    # Check if image already exists
    if unique_class in content:
        console.print(f"[dim]Image {image_id} ({unique_class}) already exists, skipping...[/dim]")
        return content
    
    # Find the section
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
        
        # Use the closest closing tag, but add spacing
        if next_p > 0 and (next_h == -1 or next_p < next_h):
            insert_pos = next_p + 4
        elif next_h > 0:
            insert_pos = next_h + 4
        
        # Get image metadata
        alt_text = metadata.get('alt_text', f'Camp Lakota {section_keyword}')
        caption = metadata.get('caption', '')
        
        # Create image HTML with unique class and better spacing
        image_html = f'\n<div class="content-image {unique_class}" style="margin: 2.5rem 0; text-align: center;">\n'
        image_html += f'<img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />\n'
        if caption:
            image_html += f'<p style="margin-top: 1rem; font-style: italic; color: #666; font-size: 0.9em; max-width: 800px; margin-left: auto; margin-right: auto;">{caption}</p>\n'
        image_html += '</div>\n'
        
        # Insert the image
        content = content[:insert_pos] + image_html + content[insert_pos:]
        console.print(f"[green]✓[/green] Inserted image {image_id} after '{section_keyword}' section")
        return content
    
    console.print(f"[yellow]⚠[/yellow] Could not find section with keyword '{section_keyword}'")
    return content


def insert_content_box(content: str, box_key: str, box_config: dict) -> str:
    """Insert a content box after a specific heading (only if not already present)"""
    
    unique_class = box_config['unique_class']
    
    # Check if box already exists
    if unique_class in content:
        console.print(f"[dim]{box_key} box already exists, skipping...[/dim]")
        return content
    
    after_text = box_config['after']
    box_html = box_config['html'].strip()
    
    # Find the heading
    pattern = rf'(<h[23]>[^<]*{re.escape(after_text)}[^<]*</h[23]>)'
    
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        insert_pos = match.end()
        # Find the end of the next paragraph with better spacing
        next_p = content.find('</p>', insert_pos)
        if next_p > 0:
            insert_pos = next_p + 4
        
        # Add spacing before box
        content = content[:insert_pos] + '\n\n' + box_html + '\n\n' + content[insert_pos:]
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
    except Exception as e:
        console.print(f"[red]Error fetching posts: {e}[/red]")
    
    console.print(f"[green]✓[/green] Built link map with {len(link_map)} entries")
    return link_map


def main():
    console.print(Panel.fit("[bold cyan]Fix & Enhance 'What to Expect' Page[/bold cyan]"))
    
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
    
    # Step 0: Remove duplicates
    console.print("\n[bold]Step 0: Removing Duplicates[/bold]")
    content = remove_duplicates(content)
    
    # Step 1: Resolve internal links (skip for now per user request)
    console.print("\n[bold]Step 1: Skipping Link Resolution[/bold]")
    console.print("[dim](Will be done after all pages are published)[/dim]")
    
    # Step 2: Insert images (idempotent)
    console.print("\n[bold]Step 2: Inserting Images (Idempotent)[/bold]")
    for image_id, keyword, unique_class in IMAGE_PLACEMENTS:
        image_url = get_image_url(session, image_id)
        if image_url:
            metadata = get_image_metadata(image_id)
            content = insert_image_after_section(content, keyword, image_id, image_url, metadata, unique_class)
        else:
            console.print(f"[yellow]⚠[/yellow] Could not get URL for image {image_id}")
    
    # Step 3: Insert content boxes (idempotent, improved placement)
    console.print("\n[bold]Step 3: Adding Content Boxes (Idempotent)[/bold]")
    for box_key, box_config in CONTENT_BOXES.items():
        content = insert_content_box(content, box_key, box_config)
    
    # Step 4: Clean up extra whitespace
    console.print("\n[bold]Step 4: Cleaning Up Formatting[/bold]")
    # Remove excessive newlines
    content = re.sub(r'\n{4,}', '\n\n', content)
    
    # Step 5: Update the page
    console.print("\n[bold]Step 5: Updating Page in WordPress[/bold]")
    
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
        console.print("[green]✅ Page updated successfully![/green]")
        console.print("\n[bold]Summary:[/bold]")
        console.print("  • Duplicates removed")
        console.print("  • Images inserted (idempotent)")
        console.print("  • Content boxes added (idempotent)")
        console.print("  • Better spacing applied")
        console.print("  • Redundant daily schedule box removed")
        console.print("  • Status: draft")
    else:
        console.print(f"[red]❌ Error updating page: {response.status_code}[/red]")
        console.print(response.text[:500])


if __name__ == '__main__':
    main()
