#!/usr/bin/env python3
"""
Convert Landing Pages to ACF Block Structure
Replicates the "Our Story" page structure using custom ACF Gutenberg blocks.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

def html_to_acf_content_block(html_content: str, padding_top: str = "pt-4", padding_bottom: str = "pb-4") -> str:
    """Convert HTML content to ACF content block format."""
    # Escape the content for JSON
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

def convert_water_sports_to_acf(session) -> str:
    """Convert Water Sports page to ACF block structure matching Our Story."""
    
    # Get current page
    response = session.get(
        Config.get_api_url('pages/806'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]Error fetching page: {response.status_code}[/red]")
        return None
    
    page = response.json()
    old_content = page.get('content', {}).get('raw', '')
    
    # Extract content sections from old HTML
    # Get the main intro paragraph
    intro_match = re.search(r'<p[^>]*>([^<]+At Camp Lakota[^<]+)</p>', old_content)
    intro_text = intro_match.group(1) if intro_match else "At Camp Lakota, water is the heart of our summer."
    
    # Build ACF block structure matching Our Story
    blocks = []
    
    # Block 1: Content with heading and intro
    intro_html = f'<h2 class="page-title">Water Sports at Camp Lakota</h2>\n{intro_text}'
    blocks.append(html_to_acf_content_block(intro_html))
    
    # Block 2: Large image (find from content or use default)
    # Extract image IDs from old content
    image_ids = re.findall(r'image_id[":\s]+(\d+)', old_content)
    if not image_ids:
        # Search for water sports images
        img_response = session.get(
            Config.get_api_url('media'),
            params={'per_page': 10, 'search': 'water'},
            timeout=30
        )
        if img_response.status_code == 200:
            media = img_response.json()
            image_ids = [str(item['id']) for item in media[:3]]
    
    if image_ids:
        blocks.append(create_large_image_block(int(image_ids[0])))
    
    # Block 3: Masten Lake Adventures section
    masten_section = '''<h2>Masten Lake Adventures</h2>
<p>Our private waterfront on Masten Lake offers a calm, safe, and exhilarating environment for campers of all ages. Under the supervision of certified boat drivers and lifeguards, campers can choose their own adventure:</p>
<ul>
<li><strong>Water Skiing & Wakeboarding:</strong> Professional instruction through private lessons helps beginners stand up and experts catch air.</li>
<li><strong>Tubing:</strong> A camp favorite! Grab a friend and hold on tight for a thrilling ride across the lake.</li>
<li><strong>Boating:</strong> Explore the shoreline at your own pace with our fleet of kayaks, canoes, rowboats, and paddleboards.</li>
<li><strong>The Aqua Park:</strong> Our inflatable water playground features slides, trampolines, and climbing obstacles right on the lake.</li>
</ul>'''
    blocks.append(html_to_acf_content_block(masten_section))
    
    # Block 4: Two column images
    if len(image_ids) >= 2:
        blocks.append(create_two_column_images_block(int(image_ids[1]), int(image_ids[2]) if len(image_ids) > 2 else int(image_ids[1])))
    
    # Block 5: Pools & Swim Instruction section
    pools_section = '''<h2>Pools & Swim Instruction</h2>
<p>Safety is our number one priority. We feature two heated swimming pools that allow for comfortable swimming regardless of the weather.</p>
<ul>
<li><strong>American Red Cross Instruction:</strong> Younger campers receive swim instruction tailored to their ability level. Our certified Water Safety Instructors (WSI) focus on stroke development, water safety, and building endurance.</li>
<li><strong>Recreational Swim:</strong> Free swim periods allow campers to play water volleyball, practice handstands, or just float with friends.</li>
<li><strong>Night Swims:</strong> On special warm evenings, we turn on the pool lights for an unforgettable experience.</li>
</ul>'''
    blocks.append(html_to_acf_content_block(pools_section))
    
    # Join all blocks
    new_content = '\n\n'.join(blocks)
    
    return new_content

def main():
    console.print(Panel.fit(
        "[bold cyan]Convert Water Sports to ACF Block Structure[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    console.print("\n[cyan]Converting Water Sports page to match Our Story structure...[/cyan]\n")
    
    new_content = convert_water_sports_to_acf(session)
    
    if not new_content:
        console.print("[red]Failed to convert content[/red]")
        return
    
    console.print("[green]✓[/green] Content converted to ACF blocks\n")
    console.print("[cyan]Preview of new structure:[/cyan]")
    console.print(new_content[:500] + "...\n")
    
    # Update page
    console.print("[cyan]Updating page in WordPress...[/cyan]")
    update_response = session.post(
        Config.get_api_url('pages/806'),
        json={
            'content': new_content,
            'template': 'template-interior.php'  # Match Our Story template
        },
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(Panel.fit(
            "[bold green]✓ Success![/bold green]\n\n"
            "Water Sports page now uses ACF blocks matching Our Story:\n"
            "  • ACF content blocks\n"
            "  • ACF large-image blocks\n"
            "  • ACF two-column-images blocks\n"
            "  • Same template as Our Story",
            border_style="green"
        ))
    else:
        console.print(f"[red]Error updating page: {update_response.status_code}[/red]")
        console.print(update_response.text)

if __name__ == '__main__':
    main()
