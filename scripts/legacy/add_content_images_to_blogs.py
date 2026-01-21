#!/usr/bin/env python3
"""
Add Content Images to Blog Posts
Inserts relevant images at natural break points in all 6 blog posts.
"""

import re
from modules.deprecation import deprecated_script_exit
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Blog post IDs and their image keywords
BLOG_POSTS = [
    {
        'id': 2701,
        'title': 'Is My Child Ready for Sleepaway Camp?',
        'keywords': ['child', 'camper', 'young', 'kids', 'ready', 'first'],
        'image_positions': ['after_intro', 'after_h2_2', 'after_h2_4']
    },
    {
        'id': 2697,
        'title': 'How Camp Counselors Support First-Time Campers',
        'keywords': ['counselor', 'staff', 'training', 'support', 'camp mom'],
        'image_positions': ['after_intro', 'after_h2_2', 'after_h2_5']
    },
    {
        'id': 2698,
        'title': 'Everything You Need to Know About Sleepaway Camp',
        'keywords': ['camp', 'camper', 'activity', 'lake', 'summer'],
        'image_positions': ['after_intro', 'after_h2_3', 'after_h2_8', 'after_h2_12']
    },
    {
        'id': 2699,
        'title': 'Sleepaway Camp Safety: What Parents Should Know',
        'keywords': ['safety', 'lifeguard', 'health', 'supervision', 'medical'],
        'image_positions': ['after_intro', 'after_h2_2', 'after_h2_5']
    },
    {
        'id': 2700,
        'title': 'Rookie Day at Camp Lakota',
        'keywords': ['rookie', 'first', 'tour', 'visit', 'experience'],
        'image_positions': ['after_intro', 'after_h2_2', 'after_h2_4']
    },
    {
        'id': 2693,
        'title': 'Packing for Sleepaway Camp',
        'keywords': ['packing', 'trunk', 'luggage', 'clothes', 'gear'],
        'image_positions': ['after_intro', 'after_h2_2', 'after_h2_5']
    },
]

def find_relevant_images(session, keywords, limit=5):
    """Find images matching keywords."""
    all_images = []
    
    for keyword in keywords:
        response = session.get(
            Config.get_api_url('media'),
            params={'per_page': 20, 'search': keyword},
            timeout=30
        )
        if response.status_code == 200:
            media = response.json()
            for img in media:
                if img.get('id') not in [i['id'] for i in all_images]:
                    all_images.append({
                        'id': img.get('id'),
                        'title': img.get('title', {}).get('rendered', ''),
                        'alt': img.get('alt_text', ''),
                        'url': img.get('source_url', '')
                    })
    
    return all_images[:limit]

def create_image_block(image_id, alignment='left', width='600'):
    """Create WordPress image block HTML."""
    return f'''<!-- wp:image {{"align":"{alignment}","width":{width},"height":400}} -->
<figure class="wp-block-image align{alignment}" style="width:{width}px"><img src="[IMAGE_URL_PLACEHOLDER]" alt="" class="wp-image-{image_id}" style="max-width:{width}px; height:auto; border-radius:8px; margin-bottom:1.5rem;"/></figure>
<!-- /wp:image -->'''

def insert_image_after_intro(content, image_block):
    """Insert image after first 2-3 paragraphs."""
    # Find first 2-3 paragraphs
    para_pattern = r'(<p[^>]*>.*?</p>)'
    paragraphs = list(re.finditer(para_pattern, content, re.DOTALL))
    
    if len(paragraphs) >= 2:
        # Insert after second paragraph
        insert_pos = paragraphs[1].end()
        # Check if there's already an image nearby
        nearby = content[max(0, insert_pos-200):insert_pos+200]
        if '<img' not in nearby and 'wp:image' not in nearby:
            return content[:insert_pos] + '\n\n' + image_block + '\n\n' + content[insert_pos:]
    
    return content

def insert_image_after_h2(content, h2_index, image_block):
    """Insert image after a specific H2 heading (0-indexed)."""
    h2_pattern = r'(<h2[^>]*>.*?</h2>)'
    h2s = list(re.finditer(h2_pattern, content, re.DOTALL))
    
    if h2_index < len(h2s):
        h2_match = h2s[h2_index]
        # Find next paragraph after this H2
        after_h2 = content[h2_match.end():]
        para_match = re.search(r'<p[^>]*>', after_h2)
        
        if para_match:
            # Insert after first paragraph following H2
            insert_pos = h2_match.end() + para_match.end()
            # Check if there's already an image nearby
            nearby = content[max(0, insert_pos-200):insert_pos+200]
            if '<img' not in nearby and 'wp:image' not in nearby:
                return content[:insert_pos] + '\n\n' + image_block + '\n\n' + content[insert_pos:]
    
    return content

def get_image_url(session, image_id):
    """Get image URL from WordPress."""
    response = session.get(
        Config.get_api_url(f'media/{image_id}'),
        timeout=30
    )
    if response.status_code == 200:
        return response.json().get('source_url', '')
    return ''

def main():
    console.print(Panel.fit(
        "[bold cyan]Add Content Images to Blog Posts[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    results = []
    
    for post_info in BLOG_POSTS:
        post_id = post_info['id']
        title = post_info['title']
        keywords = post_info['keywords']
        positions = post_info['image_positions']
        
        console.print(f"\n[cyan]Processing: {title}[/cyan]")
        
        # Get post content
        response = session.get(
            Config.get_api_url(f'posts/{post_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code != 200:
            console.print(f"  [red]✗ Error fetching post {post_id}[/red]")
            continue
        
        post = response.json()
        content = post.get('content', {}).get('raw', '')
        
        # Find relevant images
        images = find_relevant_images(session, keywords, limit=len(positions))
        
        if not images:
            console.print(f"  [yellow]⚠ No images found for keywords: {', '.join(keywords)}[/yellow]")
            results.append({
                'title': title,
                'status': 'no_images',
                'images_added': 0
            })
            continue
        
        console.print(f"  [green]✓ Found {len(images)} relevant images[/green]")
        
        # Insert images at specified positions
        new_content = content
        images_added = 0
        
        for i, position in enumerate(positions):
            if i >= len(images):
                break
            
            image = images[i]
            image_url = get_image_url(session, image['id'])
            
            if not image_url:
                continue
            
            # Create image block with actual URL
            image_block = f'''<!-- wp:image {{"align":"left","width":600,"height":400}} -->
<figure class="wp-block-image alignleft" style="width:600px"><img src="{image_url}" alt="{image['alt']}" class="wp-image-{image['id']}" style="max-width:600px; height:auto; border-radius:8px; margin-bottom:1.5rem; margin-right:1.5rem;"/></figure>
<!-- /wp:image -->'''
            
            if position == 'after_intro':
                new_content = insert_image_after_intro(new_content, image_block)
            elif position.startswith('after_h2_'):
                h2_index = int(position.split('_')[-1]) - 1  # Convert to 0-indexed
                new_content = insert_image_after_h2(new_content, h2_index, image_block)
            
            if new_content != content:
                images_added += 1
        
        # Update post if images were added
        if images_added > 0:
            update_response = session.post(
                Config.get_api_url(f'posts/{post_id}'),
                json={'content': new_content},
                timeout=30
            )
            
            if update_response.status_code == 200:
                console.print(f"  [green]✓ Added {images_added} images[/green]")
                results.append({
                    'title': title,
                    'status': 'success',
                    'images_added': images_added
                })
            else:
                console.print(f"  [red]✗ Error updating post: {update_response.status_code}[/red]")
                results.append({
                    'title': title,
                    'status': 'update_error',
                    'images_added': images_added
                })
        else:
            console.print(f"  [yellow]⚠ No images inserted (may already exist)[/yellow]")
            results.append({
                'title': title,
                'status': 'no_insert',
                'images_added': 0
            })
    
    # Summary
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]Summary[/bold green]",
        border_style="green"
    ))
    
    table = Table(title="Results")
    table.add_column("Post", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Images Added", style="green")
    
    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "⚠"
        table.add_row(
            result['title'][:40] + "..." if len(result['title']) > 40 else result['title'],
            f"{status_icon} {result['status']}",
            str(result['images_added'])
        )
    
    console.print(table)
    
    total_added = sum(r['images_added'] for r in results)
    console.print(f"\n[bold]Total images added: {total_added}[/bold]")

if __name__ == '__main__':
    deprecated_script_exit(
        "add_content_images_to_blogs.py",
        "python3 publish_content_item.py /abs/path/to/content/posts/<file>.json --type posts",
    )
    main()
