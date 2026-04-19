#!/usr/bin/env python3
"""
Update Water Sports Landing Page
Adds hero section, images, and CTA according to landing page design template.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

PAGE_ID = 806
PAGE_TITLE = "Water Sports"

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
        console.print(f"[yellow]Warning: Could not get image {image_id}: {e}[/yellow]")
    return ''

def add_hero_section(content: str, hero_image_url: str = '') -> str:
    """Add hero section with overlay banner at the beginning of content."""
    
    # Check if hero already exists
    if 'hero-section' in content.lower() or 'hero-overlay' in content.lower():
        console.print("[dim]Hero section already exists, skipping...[/dim]")
        return content
    
    # Default hero image if none provided
    if not hero_image_url:
        hero_image_url = 'https://www.camplakota.com/wp-content/uploads/2024/01/water-sports-hero.jpg'
    
    hero_html = f'''<div class="hero-section" style="position: relative; margin-bottom: 3rem;">
  <img src="{hero_image_url}" alt="Water Sports at Camp Lakota" style="width: 100%; height: auto; display: block; max-height: 500px; object-fit: cover; border-radius: 8px;">
  <div class="hero-overlay" style="position: absolute; bottom: 20px; right: 20px; background: #1a3a5c; color: white; padding: 1rem 2rem; font-size: 1.5rem; font-weight: bold; border-radius: 4px;">
    Water Sports
  </div>
</div>

'''
    
    return hero_html + content

def add_images_to_content(content: str, image_ids: list, session) -> str:
    """Add images at natural break points in content."""
    
    # Check if images already exist
    if len(re.findall(r'<img[^>]*class="[^"]*water-sports-image', content)) >= 2:
        console.print("[dim]Images already exist, skipping...[/dim]")
        return content
    
    # Find first H2 section to add image after
    h2_pattern = r'(<h2[^>]*>.*?</h2>)'
    matches = list(re.finditer(h2_pattern, content, re.DOTALL))
    
    if not matches or len(image_ids) == 0:
        console.print("[yellow]Warning: No H2 sections or images found for placement[/yellow]")
        return content
    
    # Add large image after first H2
    if len(matches) > 0 and len(image_ids) > 0:
        first_h2_end = matches[0].end()
        image_url = get_image_url(session, image_ids[0])
        if image_url:
            large_image = f'''
<div class="large-image-block" style="padding: 1rem 0; margin: 2rem 0;">
  <img src="{image_url}" alt="Water sports at Camp Lakota" class="water-sports-image-1" style="width: 100%; max-height: 500px; object-fit: cover; border-radius: 8px; display: block;">
</div>
'''
            content = content[:first_h2_end] + large_image + content[first_h2_end:]
    
    # Add side-by-side images after second H2 (if exists)
    if len(matches) > 1 and len(image_ids) > 1:
        second_h2_end = matches[1].end()
        if len(image_ids) >= 2:
            img1_url = get_image_url(session, image_ids[1])
            img2_url = get_image_url(session, image_ids[2]) if len(image_ids) > 2 else img1_url
            
            if img1_url:
                side_by_side = f'''
<div class="side-by-side-images" style="display: flex; gap: 1rem; margin: 2rem 0; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 300px;">
    <img src="{img1_url}" alt="Camp Lakota water activities" class="water-sports-image-2" style="width: 100%; height: auto; border-radius: 8px;">
  </div>
  <div style="flex: 1; min-width: 300px;">
    <img src="{img2_url}" alt="Camp Lakota water sports" class="water-sports-image-3" style="width: 100%; height: auto; border-radius: 8px;">
  </div>
</div>
'''
                content = content[:second_h2_end] + side_by_side + content[second_h2_end:]
    
    return content

def add_cta_section(content: str) -> str:
    """Add CTA section at the end of content."""
    
    # Check if CTA already exists
    if 'cta-section' in content.lower() or 'Are You Ready For The Perfect Summer' in content:
        console.print("[dim]CTA section already exists, skipping...[/dim]")
        return content
    
    cta_html = '''
<div class="cta-section" style="background: #f8f9fa; padding: 3rem 2rem; margin: 3rem 0; text-align: center;">
  <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.5rem;">
    <span style="font-size: 2rem;">☀️</span>
    <h3 style="margin: 0; font-size: 1.75rem; font-weight: bold;">Are You Ready For The Perfect Summer?</h3>
  </div>
  <div style="background: #1a3a5c; padding: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
    <a href="https://www.camplakota.com/contact-us/" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      📧 REQUEST INFO
    </a>
    <a href="https://www.camplakota.com/enroll-now/" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      ✓ ENROLL NOW
    </a>
    <a href="https://www.camplakota.com/dates-tuition/" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      📅 DATES & TUITION
    </a>
  </div>
</div>
'''
    
    return content + cta_html

def main():
    console.print(Panel.fit(
        f"[bold cyan]Update {PAGE_TITLE} Landing Page[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get current page
    console.print(f"\n[cyan]Fetching page {PAGE_ID}...[/cyan]")
    response = session.get(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return
    
    page = response.json()
    content = page.get('content', {}).get('raw', '')
    
    console.print(f"[green]✓[/green] Page loaded ({len(content)} characters)\n")
    
    # Search for relevant images
    console.print("[cyan]Searching for water sports images...[/cyan]")
    image_ids = []
    
    # Try to find images related to water sports
    search_terms = ['water', 'swim', 'lake', 'kayak', 'canoe', 'sail', 'tubing', 'waterski']
    for term in search_terms:
        img_response = session.get(
            Config.get_api_url('media'),
            params={'per_page': 10, 'search': term},
            timeout=30
        )
        if img_response.status_code == 200:
            media = img_response.json()
            for item in media[:3]:  # Take first 3
                if item['id'] not in image_ids:
                    image_ids.append(item['id'])
                    if len(image_ids) >= 3:
                        break
        if len(image_ids) >= 3:
            break
    
    if not image_ids:
        # Use some default images if none found
        console.print("[yellow]No specific images found, will use fallback[/yellow]")
        image_ids = [2626, 2581, 1048]  # Fallback images
    
    console.print(f"[green]✓[/green] Found {len(image_ids)} images\n")
    
    # Update content
    console.print("[cyan]Adding hero section...[/cyan]")
    content = add_hero_section(content)
    
    console.print("[cyan]Adding images...[/cyan]")
    content = add_images_to_content(content, image_ids, session)
    
    console.print("[cyan]Adding CTA section...[/cyan]")
    content = add_cta_section(content)
    
    # Update page
    console.print(f"\n[cyan]Updating page in WordPress...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'pages/{PAGE_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(Panel.fit(
            f"[bold green]✓ Success![/bold green]\n\n"
            f"Updated {PAGE_TITLE} page with:\n"
            f"  • Hero section with overlay banner\n"
            f"  • {len(image_ids)} images\n"
            f"  • CTA section with buttons",
            border_style="green"
        ))
    else:
        console.print(f"[red]Error updating page: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
