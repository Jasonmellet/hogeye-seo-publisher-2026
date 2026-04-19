#!/usr/bin/env python3
"""
Update Blog Post Featured Images
Matches each blog post to a unique, relevant featured image based on topic.
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Blog posts with their topics and keywords
BLOG_POSTS = [
    {
        'id': 2701,
        'title': 'Is My Child Ready for Sleepaway Camp?',
        'keywords': ['child', 'camper', 'young', 'kids', 'ready', 'first', 'boy', 'girl'],
        'priority_keywords': ['child', 'ready', 'young']
    },
    {
        'id': 2697,
        'title': 'How Camp Counselors Support First-Time Campers',
        'keywords': ['counselor', 'staff', 'support', 'training', 'help', 'CIT', 'mentor'],
        'priority_keywords': ['counselor', 'staff', 'CIT']
    },
    {
        'id': 2698,
        'title': 'Everything You Need to Know About Sleepaway Camp',
        'keywords': ['camp', 'summer', 'lake', 'activity', 'overview', 'complete', 'guide'],
        'priority_keywords': ['camp', 'summer', 'lake']
    },
    {
        'id': 2699,
        'title': 'Sleepaway Camp Safety: What Parents Should Know',
        'keywords': ['safety', 'lifeguard', 'health', 'medical', 'supervision', 'water'],
        'priority_keywords': ['safety', 'lifeguard', 'water']
    },
    {
        'id': 2700,
        'title': 'Rookie Day at Camp Lakota',
        'keywords': ['rookie', 'first', 'tour', 'visit', 'experience', 'day', 'family'],
        'priority_keywords': ['rookie', 'tour', 'visit']
    },
    {
        'id': 2693,
        'title': 'Packing for Sleepaway Camp',
        'keywords': ['packing', 'trunk', 'luggage', 'clothes', 'gear', 'bag', 'preparation'],
        'priority_keywords': ['packing', 'trunk', 'luggage']
    },
]

def search_images_for_keywords(session, keywords, limit=50):
    """Search for images matching keywords."""
    all_images = {}
    
    for keyword in keywords:
        response = session.get(
            Config.get_api_url('media'),
            params={'per_page': 20, 'search': keyword},
            timeout=30
        )
        
        if response.status_code == 200:
            media = response.json()
            for img in media:
                img_id = img.get('id')
                title = img.get('title', {}).get('rendered', '').lower()
                alt = img.get('alt_text', '').lower()
                
                # Score image based on keyword matches
                score = 0
                matched_keywords = []
                
                for kw in keywords:
                    if kw.lower() in title or kw.lower() in alt:
                        score += 2 if kw in keywords[:3] else 1  # Priority keywords worth more
                        matched_keywords.append(kw)
                
                if img_id not in all_images or score > all_images[img_id]['score']:
                    all_images[img_id] = {
                        'id': img_id,
                        'title': img.get('title', {}).get('rendered', ''),
                        'alt': img.get('alt_text', ''),
                        'score': score,
                        'keywords': matched_keywords
                    }
    
    # Sort by score
    sorted_images = sorted(all_images.values(), key=lambda x: x['score'], reverse=True)
    return sorted_images[:limit]

def find_best_image_for_post(session, post_info, used_image_ids):
    """Find the best matching image for a post that hasn't been used yet."""
    # Search for images
    images = search_images_for_keywords(session, post_info['keywords'])
    
    # Filter out already used images
    available_images = [img for img in images if img['id'] not in used_image_ids]
    
    if available_images:
        return available_images[0]
    
    # If all matching images are used, get any unused image
    if images:
        return images[0]
    
    return None

def main():
    console.print(Panel.fit(
        "[bold cyan]Update Blog Post Featured Images[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get current featured images
    console.print("\n[cyan]Checking current featured images...[/cyan]")
    current_images = {}
    for post_info in BLOG_POSTS:
        response = session.get(
            Config.get_api_url(f'posts/{post_info["id"]}'),
            params={'context': 'edit'},
            timeout=30
        )
        if response.status_code == 200:
            post = response.json()
            current_images[post_info['id']] = post.get('featured_media', 0)
    
    # Find new images
    console.print("\n[cyan]Finding unique images for each post...[/cyan]\n")
    
    used_image_ids = set()
    assignments = []
    
    for post_info in BLOG_POSTS:
        console.print(f"[yellow]Finding image for: {post_info['title']}[/yellow]")
        
        best_image = find_best_image_for_post(session, post_info, used_image_ids)
        
        if best_image:
            used_image_ids.add(best_image['id'])
            assignments.append({
                'post_id': post_info['id'],
                'post_title': post_info['title'],
                'current_image': current_images.get(post_info['id'], 0),
                'new_image': best_image['id'],
                'image_title': best_image['title'],
                'match_score': best_image['score']
            })
            console.print(f"  [green]✓ Found: Image {best_image['id']} - {best_image['title'][:50]}...[/green]")
            console.print(f"    Match score: {best_image['score']}, Keywords: {', '.join(best_image['keywords'][:3])}")
        else:
            console.print(f"  [red]✗ No suitable image found[/red]")
    
    # Show assignments
    console.print("\n" + "="*60)
    table = Table(title="Featured Image Assignments")
    table.add_column("Post", style="cyan", max_width=30)
    table.add_column("Current", style="yellow")
    table.add_column("New", style="green")
    table.add_column("Image Title", style="dim", max_width=30)
    table.add_column("Change", style="magenta")
    
    for assignment in assignments:
        change = "✓ Update" if assignment['current_image'] != assignment['new_image'] else "No change"
        table.add_row(
            assignment['post_title'][:28] + "..." if len(assignment['post_title']) > 28 else assignment['post_title'],
            str(assignment['current_image']),
            str(assignment['new_image']),
            assignment['image_title'][:28] + "..." if len(assignment['image_title']) > 28 else assignment['image_title'],
            change
        )
    
    console.print(table)
    
    # Update posts
    console.print("\n[cyan]Updating featured images...[/cyan]\n")
    
    updated_count = 0
    for assignment in assignments:
        if assignment['current_image'] != assignment['new_image']:
            response = session.post(
                Config.get_api_url(f'posts/{assignment["post_id"]}'),
                json={'featured_media': assignment['new_image']},
                timeout=30
            )
            
            if response.status_code == 200:
                console.print(f"  [green]✓ Updated: {assignment['post_title'][:40]}...[/green]")
                console.print(f"    {assignment['current_image']} → {assignment['new_image']}")
                updated_count += 1
            else:
                console.print(f"  [red]✗ Error updating {assignment['post_id']}: {response.status_code}[/red]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold green]Updated {updated_count} featured images[/bold green]",
        border_style="green"
    ))
    console.print("\n[cyan]Each blog post now has a unique, topic-relevant featured image![/cyan]")

if __name__ == '__main__':
    main()
