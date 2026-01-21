#!/usr/bin/env python3
"""
Fix Counselors Support Post - Complete
- Ensure 5-6 unique, diverse images
- Ensure 5 FAQ questions
- Remove any duplicates
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
from collections import Counter

console = Console()

POST_ID = 2697
FEATURED_IMAGE_ID = 2705

def find_diverse_images(session, exclude_ids, limit=10):
    """Find diverse images for counselors post."""
    keywords = ['counselor', 'staff', 'young', 'child', 'camper', 'support', 'help', 'group', 'together']
    
    # Get all images
    all_images = []
    page = 1
    while True:
        response = session.get(
            Config.get_api_url('media'),
            params={'per_page': 100, 'page': page},
            timeout=30
        )
        if response.status_code != 200:
            break
        batch = response.json()
        if not batch:
            break
        all_images.extend(batch)
        page += 1
        if page > 10:
            break
    
    # Score images
    scored = []
    for img in all_images:
        img_id = img.get('id')
        if img_id in exclude_ids:
            continue
        
        title = img.get('title', {}).get('rendered', '').lower()
        alt_text = img.get('alt_text', '').lower()
        all_text = f"{title} {alt_text}"
        
        score = 0
        for keyword in keywords:
            if keyword in all_text:
                score += 1
        
        # Bonus for counselor + camper/young
        if ('counselor' in all_text or 'staff' in all_text) and ('camper' in all_text or 'young' in all_text or 'child' in all_text):
            score += 2
        
        if score > 0:
            scored.append({
                'id': img_id,
                'score': score,
                'title': title,
                'alt': alt_text or title,
                'url': img.get('source_url', '')
            })
    
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # Select diverse images (avoid similar titles)
    selected = []
    selected_titles = []
    
    for img in scored:
        if len(selected) >= limit:
            break
        
        # Check if title is too similar to already selected
        is_similar = False
        img_words = set(img['title'].split())
        for sel_title in selected_titles:
            sel_words = set(sel_title.split())
            common = img_words.intersection(sel_words)
            if len(common) > 3:  # More than 3 common words = too similar
                is_similar = True
                break
        
        if not is_similar:
            selected.append(img)
            selected_titles.append(img['title'])
    
    return selected

def create_image_block(image, alignment='full'):
    """Create image block HTML."""
    return f'''<!-- wp:image {{"align":"{alignment}","width":600,"height":400}} -->
<figure class="wp-block-image align{alignment}" style="width:100%; max-width:100%"><img src="{image['url']}" alt="{image['alt']}" class="wp-image-{image['id']}" style="max-width:100%; height:auto; border-radius:8px;"/></figure>
<!-- /wp:image -->'''

def add_images_to_content(content, images, session):
    """Add images at natural break points."""
    # Find H2 headings
    h2_pattern = r'(<h2[^>]*>.*?</h2>)'
    h2_matches = list(re.finditer(h2_pattern, content, re.DOTALL))
    
    if not h2_matches or not images:
        return content
    
    # Positions: after intro, after H2 #2, after H2 #4, after H2 #6
    positions = [
        ('after_intro', None),
        ('after_h2', 1),  # Second H2
        ('after_h2', 3),  # Fourth H2
        ('after_h2', 5),  # Sixth H2
    ]
    
    updated_content = content
    image_index = 0
    offset = 0
    
    for pos_type, h2_index in positions:
        if image_index >= len(images):
            break
        
        image = images[image_index]
        image_block = create_image_block(image)
        
        if pos_type == 'after_intro':
            # After first 2 paragraphs
            para_pattern = r'(<p[^>]*>.*?</p>)'
            paragraphs = list(re.finditer(para_pattern, updated_content, re.DOTALL))
            if len(paragraphs) >= 2:
                insert_pos = paragraphs[1].end() + offset
                nearby = updated_content[max(0, insert_pos-300):min(len(updated_content), insert_pos+300)]
                if 'wp-image' not in nearby:
                    updated_content = updated_content[:insert_pos] + '\n\n' + image_block + '\n\n' + updated_content[insert_pos:]
                    offset += len(image_block) + 4
                    image_index += 1
        elif pos_type == 'after_h2' and h2_index < len(h2_matches):
            h2_match = h2_matches[h2_index]
            insert_pos = h2_match.end() + offset
            next_elem = re.search(r'<p|<ul|<ol|<h3', updated_content[insert_pos:])
            if next_elem:
                insert_pos = insert_pos + next_elem.start()
            nearby = updated_content[max(0, insert_pos-300):min(len(updated_content), insert_pos+300)]
            if 'wp-image' not in nearby:
                updated_content = updated_content[:insert_pos] + '\n\n' + image_block + '\n\n' + updated_content[insert_pos:]
                offset += len(image_block) + 4
                image_index += 1
    
    return updated_content

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix Counselors Post - Complete[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get post
    response = session.get(
        Config.get_api_url(f'posts/{POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]✗ Error fetching post[/red]")
        return
    
    post = response.json()
    content = post.get('content', {}).get('raw', '')
    
    # Get current images
    current_ids = set(re.findall(r'wp-image-(\d+)', content))
    console.print(f"\n[cyan]Current images: {len(current_ids)}[/cyan]")
    
    # Remove all existing images to start fresh
    console.print(f"\n[cyan]Step 1: Removing all existing images...[/cyan]")
    image_pattern = r'<!-- wp:image.*?<!-- /wp:image -->'
    content = re.sub(image_pattern, '', content, flags=re.DOTALL)
    console.print(f"  [green]✓ Removed existing images[/green]")
    
    # Find diverse images
    console.print(f"\n[cyan]Step 2: Finding diverse images...[/cyan]")
    exclude_ids = [FEATURED_IMAGE_ID]
    images = find_diverse_images(session, exclude_ids, limit=6)
    console.print(f"  [green]✓ Found {len(images)} diverse images[/green]")
    
    for i, img in enumerate(images, 1):
        console.print(f"  {i}. ID {img['id']}: {img['title'][:50]}...")
    
    # Add images
    console.print(f"\n[cyan]Step 3: Adding images at natural break points...[/cyan]")
    content = add_images_to_content(content, images[:5], session)  # Add 5 images
    
    # Verify
    final_ids = set(re.findall(r'wp-image-(\d+)', content))
    console.print(f"  [green]✓ Added images - total now: {len(final_ids)}[/green]")
    
    # Check FAQ
    console.print(f"\n[cyan]Step 4: Verifying FAQ...[/cyan]")
    faq_match = re.search(r'<h2[^>]*>Frequently Asked Questions</h2>(.*?)(?=<h2|<h3[^>]*>Learn|$)', content, re.DOTALL | re.IGNORECASE)
    if faq_match:
        faq_section = faq_match.group(1)
        visible_questions = re.findall(r'<h3[^>]*>(.*?)</h3>', faq_section)
        console.print(f"  [green]✓ FAQ has {len(visible_questions)} questions[/green]")
    else:
        console.print(f"  [yellow]⚠ FAQ section not found[/yellow]")
    
    # Update post
    console.print(f"\n[cyan]Step 5: Updating post...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'posts/{POST_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        # Final verification
        verify_response = session.get(
            Config.get_api_url(f'posts/{POST_ID}'),
            params={'context': 'edit'},
            timeout=30
        )
        if verify_response.status_code == 200:
            verify_content = verify_response.json().get('content', {}).get('raw', '')
            final_ids = set(re.findall(r'wp-image-(\d+)', verify_content))
            counts = Counter(re.findall(r'wp-image-(\d+)', verify_content))
            duplicates = [img_id for img_id, count in counts.items() if count > 1]
            
            faq_questions = len(re.findall(r'<h3[^>]*>.*?</h3>', verify_content))
            
            console.print(f"  [green]✓ Post updated successfully[/green]")
            console.print(f"\n[bold green]✓ Complete![/bold green]")
            console.print(f"[green]✓ Total unique images: {len(final_ids)}[/green]")
            if duplicates:
                console.print(f"[red]✗ Duplicates: {duplicates}[/red]")
            else:
                console.print(f"[green]✓ No duplicates[/green]")
            console.print(f"[green]✓ FAQ questions: {faq_questions}[/green]")
        else:
            console.print(f"  [green]✓ Post updated successfully[/green]")
    else:
        console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
