#!/usr/bin/env python3
"""
Fix Counselors Support Post
- Remove duplicate images
- Add more images at natural break points
- Ensure FAQ has all questions
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

def find_relevant_images(session, keywords, exclude_ids=None, limit=10):
    """Find images matching keywords."""
    if exclude_ids is None:
        exclude_ids = []
    
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
        caption = img.get('caption', {}).get('rendered', '').lower()
        
        all_text = f"{title} {alt_text} {caption}"
        
        score = 0
        matched = []
        for keyword in keywords:
            if keyword in all_text:
                score += 1
                matched.append(keyword)
        
        # Bonus for counselor + camper/young/child
        if ('counselor' in all_text or 'staff' in all_text) and ('camper' in all_text or 'young' in all_text or 'child' in all_text):
            score += 2
        
        if score > 0:
            scored.append({
                'id': img_id,
                'score': score,
                'keywords': matched,
                'title': title,
                'alt': alt_text or title,
                'url': img.get('source_url', '')
            })
    
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:limit]

def remove_duplicate_images(content):
    """Remove duplicate images, keeping only the first occurrence of each."""
    # Find all image blocks
    image_pattern = r'(<!-- wp:image.*?<!-- /wp:image -->)'
    matches = list(re.finditer(image_pattern, content, re.DOTALL))
    
    seen_ids = set()
    to_remove = []
    
    for match in matches:
        block = match.group(0)
        img_id_match = re.search(r'wp-image-(\d+)', block)
        if img_id_match:
            img_id = int(img_id_match.group(1))
            if img_id in seen_ids:
                to_remove.append(match)
            else:
                seen_ids.add(img_id)
    
    # Remove duplicates (in reverse order to maintain positions)
    updated_content = content
    for match in reversed(to_remove):
        updated_content = updated_content[:match.start()] + updated_content[match.end():]
    
    return updated_content, len(to_remove)

def add_images_at_break_points(content, images, session):
    """Add images at natural break points (after H2s, after intro)."""
    # Find H2 headings
    h2_pattern = r'(<h2[^>]*>.*?</h2>)'
    h2_matches = list(re.finditer(h2_pattern, content, re.DOTALL))
    
    if not h2_matches or not images:
        return content
    
    # Positions to add images: after intro, after H2 #2, after H2 #4, after H2 #6
    positions = [
        ('after_intro', None),
        ('after_h2', 1),  # Second H2 (index 1)
        ('after_h2', 3),  # Fourth H2 (index 3)
        ('after_h2', 5),  # Sixth H2 (index 5)
    ]
    
    updated_content = content
    image_index = 0
    offset = 0
    
    for pos_type, h2_index in positions:
        if image_index >= len(images):
            break
        
        image = images[image_index]
        
        # Create image block
        image_block = f'''<!-- wp:image {{"align":"full","width":600,"height":400}} -->
<figure class="wp-block-image alignfull" style="width:100%; max-width:100%"><img src="{image['url']}" alt="{image['alt']}" class="wp-image-{image['id']}" style="max-width:100%; height:auto; border-radius:8px;"/></figure>
<!-- /wp:image -->'''
        
        if pos_type == 'after_intro':
            # Find first 2-3 paragraphs
            para_pattern = r'(<p[^>]*>.*?</p>)'
            paragraphs = list(re.finditer(para_pattern, updated_content, re.DOTALL))
            if len(paragraphs) >= 2:
                insert_pos = paragraphs[1].end() + offset
                # Check if image already exists nearby
                nearby = updated_content[max(0, insert_pos-300):min(len(updated_content), insert_pos+300)]
                if 'wp-image' not in nearby:
                    updated_content = updated_content[:insert_pos] + '\n\n' + image_block + '\n\n' + updated_content[insert_pos:]
                    offset += len(image_block) + 4
                    image_index += 1
        elif pos_type == 'after_h2' and h2_index < len(h2_matches):
            h2_match = h2_matches[h2_index]
            insert_pos = h2_match.end() + offset
            # Find next paragraph or element
            next_elem = re.search(r'<p|<ul|<ol|<h3', updated_content[insert_pos:])
            if next_elem:
                insert_pos = insert_pos + next_elem.start()
            # Check if image already exists nearby
            nearby = updated_content[max(0, insert_pos-300):min(len(updated_content), insert_pos+300)]
            if 'wp-image' not in nearby:
                updated_content = updated_content[:insert_pos] + '\n\n' + image_block + '\n\n' + updated_content[insert_pos:]
                offset += len(image_block) + 4
                image_index += 1
    
    return updated_content

def ensure_complete_faq(content):
    """Ensure FAQ section has all questions from source."""
    # Expected FAQ questions from add_faq_to_remaining_blogs.py
    expected_faqs = [
        {
            'question': 'What qualifications do Camp Lakota counselors have?',
            'answer': 'All Camp Lakota counselors undergo rigorous background checks, mandatory sexual abuse prevention training, reference verification, and comprehensive interviews. Once at camp, staff complete a week-long orientation covering child development, safety protocols, homesickness management, and camp culture. Many counselors hold certifications in lifeguarding, first aid, or activity-specific areas.'
        },
        {
            'question': 'How do counselors help with homesickness?',
            'answer': 'Our counselors are specifically trained to handle homesickness through normalization, engagement, and support. They help campers by normalizing feelings without amplifying them, keeping campers engaged in activities, creating social connections, and watching for patterns. If homesickness persists beyond 72 hours, directors step in with additional strategies and parent communication.'
        },
        {
            'question': 'What is the staff-to-camper ratio at Camp Lakota?',
            'answer': 'Camp Lakota maintains staff-to-camper ratios that exceed industry standards, ensuring adequate supervision for all activities. Our youngest divisions have additional support through "Camp Moms"—experienced parents who provide extra supervision and comfort for first-time younger campers.'
        },
        {
            'question': 'How do counselors handle campers who are shy or reluctant to participate?',
            'answer': 'Counselors use proximity and modeling rather than forcing participation. They sit near reluctant campers, participate in activities themselves, and create low-pressure invitations. Counselors respect boundaries while keeping doors open for future participation. This approach helps shy campers feel included without pressure.'
        },
        {
            'question': 'Can I communicate directly with my child\'s counselor?',
            'answer': 'For routine questions and concerns, we recommend contacting camp directors rather than counselors directly. This ensures consistent communication and allows directors to coordinate with counselors appropriately. In emergencies or urgent situations, directors will facilitate communication as needed.'
        }
    ]
    
    # Check if FAQ exists
    faq_match = re.search(r'<h2[^>]*>Frequently Asked Questions</h2>(.*?)(?=<h2|<h3[^>]*>Learn|$)', content, re.DOTALL | re.IGNORECASE)
    
    if faq_match:
        faq_section = faq_match.group(1)
        existing_questions = re.findall(r'<h3[^>]*>(.*?)</h3>', faq_section)
        
        if len(existing_questions) < len(expected_faqs):
            console.print(f"[yellow]⚠ FAQ has {len(existing_questions)} questions, expected {len(expected_faqs)}[/yellow]")
            
            # Rebuild FAQ section
            import json
            schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": []
            }
            
            faq_html = '\n\n'
            for item in expected_faqs:
                schema["mainEntity"].append({
                    "@type": "Question",
                    "name": item['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item['answer']
                    }
                })
                
                faq_html += f'''<div class="faq-item" style="margin-bottom: 2rem;">
<h3 style="margin-top: 2rem; margin-bottom: 1rem; font-weight: bold;">{item['question']}</h3>
<p style="margin-bottom: 1.5rem; line-height: 1.7;">{item['answer']}</p>
</div>

'''
            
            schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
            new_faq = f'<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem;">Frequently Asked Questions</h2>\n\n<script type="application/ld+json">\n{schema_json}\n</script>\n\n{faq_html}'
            
            # Replace existing FAQ
            faq_start = faq_match.start()
            faq_end = faq_match.end()
            content = content[:faq_start] + new_faq + content[faq_end:]
            
            return content, True
    
    return content, False

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix Counselors Support Post[/bold cyan]",
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
        console.print(f"[red]✗ Error fetching post {POST_ID}[/red]")
        return
    
    post = response.json()
    content = post.get('content', {}).get('raw', '')
    
    console.print(f"\n[cyan]Step 1: Removing duplicate images...[/cyan]")
    content, removed_count = remove_duplicate_images(content)
    if removed_count > 0:
        console.print(f"  [green]✓ Removed {removed_count} duplicate images[/green]")
    else:
        console.print(f"  [green]✓ No duplicates found[/green]")
    
    # Count current images
    current_images = len(re.findall(r'wp-image-(\d+)', content))
    console.print(f"  [cyan]Current images: {current_images}[/cyan]")
    
    console.print(f"\n[cyan]Step 2: Finding relevant images...[/cyan]")
    keywords = ['counselor', 'staff', 'young', 'child', 'camper', 'support', 'help', 'first', 'training']
    images = find_relevant_images(session, keywords, exclude_ids=[FEATURED_IMAGE_ID], limit=8)
    console.print(f"  [green]✓ Found {len(images)} relevant images[/green]")
    
    # Get unique images (exclude ones already in content)
    existing_ids = set(re.findall(r'wp-image-(\d+)', content))
    new_images = [img for img in images if img['id'] not in existing_ids]
    console.print(f"  [green]✓ {len(new_images)} new images available[/green]")
    
    console.print(f"\n[cyan]Step 3: Adding images at natural break points...[/cyan]")
    if new_images:
        content = add_images_at_break_points(content, new_images[:4], session)  # Add up to 4 more
        new_count = len(re.findall(r'wp-image-(\d+)', content))
        console.print(f"  [green]✓ Added images - total now: {new_count}[/green]")
    else:
        console.print(f"  [yellow]⚠ No new images to add[/yellow]")
    
    console.print(f"\n[cyan]Step 4: Ensuring complete FAQ...[/cyan]")
    content, faq_updated = ensure_complete_faq(content)
    if faq_updated:
        console.print(f"  [green]✓ FAQ section updated[/green]")
    else:
        console.print(f"  [green]✓ FAQ section verified[/green]")
    
    # Final check for duplicates
    all_img_ids = re.findall(r'wp-image-(\d+)', content)
    counts = Counter(all_img_ids)
    duplicates = [img_id for img_id, count in counts.items() if count > 1]
    
    if duplicates:
        console.print(f"\n[yellow]⚠ Still found duplicates: {duplicates}[/yellow]")
        # Remove remaining duplicates
        seen = set()
        for img_id in duplicates:
            pattern = r'(<!-- wp:image.*?wp-image-' + str(img_id) + r'.*?<!-- /wp:image -->)'
            matches = list(re.finditer(pattern, content, re.DOTALL))
            for i, match in enumerate(matches):
                if i == 0:
                    seen.add(img_id)
                else:
                    content = content[:match.start()] + content[match.end():]
    
    console.print(f"\n[cyan]Step 5: Updating post...[/cyan]")
    update_response = session.post(
        Config.get_api_url(f'posts/{POST_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        # Verify
        verify_response = session.get(
            Config.get_api_url(f'posts/{POST_ID}'),
            params={'context': 'edit'},
            timeout=30
        )
        if verify_response.status_code == 200:
            verify_post = verify_response.json()
            verify_content = verify_post.get('content', {}).get('raw', '')
            
            final_images = len(set(re.findall(r'wp-image-(\d+)', verify_content)))
            faq_questions = len(re.findall(r'<h3[^>]*>.*?</h3>', verify_content))
            
            console.print(f"  [green]✓ Post updated successfully[/green]")
            console.print(f"\n[bold green]✓ Complete![/bold green]")
            console.print(f"[green]✓ Total unique images: {final_images}[/green]")
            console.print(f"[green]✓ FAQ questions: {faq_questions}[/green]")
        else:
            console.print(f"  [green]✓ Post updated successfully[/green]")
    else:
        console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")

if __name__ == '__main__':
    main()
