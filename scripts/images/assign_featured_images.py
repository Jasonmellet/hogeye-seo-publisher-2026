#!/usr/bin/env python3
"""
Assign featured images to blog posts based on metadata matching
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Blog post to featured image mapping
# Based on keyword matching and relevance
FEATURED_IMAGE_ASSIGNMENTS = {
    2701: {  # Is My Child Ready
        'image_id': 2702,
        'reason': 'Young campers - matches first-time camper theme'
    },
    2697: {  # Counselors Support
        'image_id': 2705,
        'reason': 'CIT counselors in training - matches counselor support theme'
    },
    2698: {  # Everything You Need to Know
        'image_id': 2626,
        'reason': 'Tubing on Masten Lake - general camp activity overview'
    },
    2699: {  # Camp Safety
        'image_id': 2706,
        'reason': 'Lifeguards with camper - matches safety theme'
    },
    2700: {  # Rookie Day
        'image_id': 1165,
        'reason': 'Rookie Day trial program - perfect match'
    },
    2693: {  # Packing Guide
        'image_id': 1805,
        'reason': 'Packing guide image - direct match'
    }
}

BLOG_POST_NAMES = {
    2701: 'Is My Child Ready',
    2697: 'Counselors Support',
    2698: 'Everything You Need to Know',
    2699: 'Camp Safety',
    2700: 'Rookie Day',
    2693: 'Packing Guide'
}


def verify_image_exists(session, image_id):
    """Verify image exists in WordPress"""
    try:
        response = session.get(
            Config.get_api_url(f'media/{image_id}'),
            timeout=30
        )
        if response.status_code == 200:
            img = response.json()
            return {
                'exists': True,
                'title': img.get('title', {}).get('rendered', ''),
                'url': img.get('source_url', '')
            }
        return {'exists': False}
    except Exception as e:
        console.print(f"[red]Error checking image {image_id}: {e}[/red]")
        return {'exists': False}


def assign_featured_image(session, post_id, image_id):
    """Assign featured image to a blog post"""
    try:
        update_data = {
            'featured_media': image_id
        }
        
        response = session.post(
            Config.get_api_url(f'posts/{post_id}'),
            json=update_data,
            timeout=30
        )
        
        return response.status_code == 200
    except Exception as e:
        console.print(f"[red]Error assigning image: {e}[/red]")
        return False


def main():
    console.print(Panel.fit(
        "[bold cyan]Assign Featured Images to Blog Posts[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Verify all images exist
    console.print("\n[bold]Step 1: Verifying Images Exist[/bold]\n")
    
    verification_table = Table(title="Image Verification")
    verification_table.add_column("Post", style="cyan")
    verification_table.add_column("Post ID", style="yellow")
    verification_table.add_column("Image ID", style="green")
    verification_table.add_column("Image Title", style="dim")
    verification_table.add_column("Status", style="dim")
    
    all_verified = True
    for post_id, assignment in FEATURED_IMAGE_ASSIGNMENTS.items():
        image_id = assignment['image_id']
        img_info = verify_image_exists(session, image_id)
        
        if img_info['exists']:
            status = "✅ Exists"
            verification_table.add_row(
                BLOG_POST_NAMES[post_id],
                str(post_id),
                str(image_id),
                img_info['title'][:50] + '...' if len(img_info['title']) > 50 else img_info['title'],
                status
            )
        else:
            status = "❌ Not Found"
            all_verified = False
            verification_table.add_row(
                BLOG_POST_NAMES[post_id],
                str(post_id),
                str(image_id),
                "N/A",
                status
            )
    
    console.print(verification_table)
    
    if not all_verified:
        console.print("\n[red]Some images not found. Please check image IDs.[/red]")
        return
    
    # Assign featured images
    console.print("\n[bold]Step 2: Assigning Featured Images[/bold]\n")
    
    results_table = Table(title="Assignment Results")
    results_table.add_column("Post", style="cyan")
    results_table.add_column("Post ID", style="yellow")
    results_table.add_column("Image ID", style="green")
    results_table.add_column("Status", style="dim")
    
    success_count = 0
    for post_id, assignment in FEATURED_IMAGE_ASSIGNMENTS.items():
        image_id = assignment['image_id']
        
        console.print(f"[dim]Assigning image {image_id} to post {post_id}...[/dim]")
        
        if assign_featured_image(session, post_id, image_id):
            status = "✅ Assigned"
            success_count += 1
        else:
            status = "❌ Failed"
        
        results_table.add_row(
            BLOG_POST_NAMES[post_id],
            str(post_id),
            str(image_id),
            status
        )
    
    console.print("\n")
    console.print(results_table)
    
    # Verify assignments
    console.print("\n[bold]Step 3: Verifying Assignments[/bold]\n")
    
    verify_table = Table(title="Verification")
    verify_table.add_column("Post", style="cyan")
    verify_table.add_column("Post ID", style="yellow")
    verify_table.add_column("Featured Image ID", style="green")
    verify_table.add_column("Status", style="dim")
    
    for post_id in FEATURED_IMAGE_ASSIGNMENTS.keys():
        response = session.get(
            Config.get_api_url(f'posts/{post_id}'),
            timeout=30
        )
        
        if response.status_code == 200:
            post = response.json()
            featured_id = post.get('featured_media', 0)
            expected_id = FEATURED_IMAGE_ASSIGNMENTS[post_id]['image_id']
            
            if featured_id == expected_id:
                status = "✅ Verified"
            elif featured_id > 0:
                status = f"⚠️ Different ({featured_id})"
            else:
                status = "❌ Not Set"
            
            verify_table.add_row(
                BLOG_POST_NAMES[post_id],
                str(post_id),
                str(featured_id) if featured_id > 0 else "None",
                status
            )
    
    console.print(verify_table)
    
    # Summary
    console.print(f"\n[bold green]✅ Featured Images Assignment Complete![/bold green]")
    console.print(f"  • {success_count} of {len(FEATURED_IMAGE_ASSIGNMENTS)} assignments successful")
    console.print(f"\n[bold]Next Steps:[/bold]")
    console.print(f"  1. Check posts in WordPress admin to verify images display correctly")
    console.print(f"  2. Preview posts to ensure featured images look good")
    console.print(f"  3. Adjust if needed (can re-run this script with different image IDs)")


if __name__ == '__main__':
    main()
