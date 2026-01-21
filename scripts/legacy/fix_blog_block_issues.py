#!/usr/bin/env python3
"""
Fix Block Issues in Blog Posts
Removes duplicate style attributes and fixes malformed HTML.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

BLOG_POSTS = [
    (2701, 'Is My Child Ready for Sleepaway Camp?'),
    (2697, 'How Camp Counselors Support First-Time Campers'),
    (2698, 'Everything You Need to Know About Sleepaway Camp'),
    (2699, 'Sleepaway Camp Safety: What Parents Should Know'),
    (2700, 'Rookie Day at Camp Lakota'),
    (2693, 'Packing for Sleepaway Camp'),
]

def fix_content(content: str) -> str:
    """Fix common block issues in content."""
    fixed = content
    
    # Fix duplicate style attributes (e.g., style="..." style="...")
    # Pattern: style="..." followed by another style="..."
    fixed = re.sub(
        r'(style="[^"]*")\s+style="([^"]*)"',
        r'style="\2"',
        fixed
    )
    
    # Fix malformed style attributes with duplicate keys
    # Pattern: style="margin-top: 2.5rem; margin-bottom: 1.5rem; style="margin-top: 2.5rem; margin-bottom: 1.5rem;"
    fixed = re.sub(
        r'style="([^"]*);\s*style="([^"]*)"',
        r'style="\1; \2"',
        fixed
    )
    
    # Fix any remaining duplicate style attributes
    fixed = re.sub(
        r'style="([^"]*)"\s+style="([^"]*)"',
        lambda m: f'style="{m.group(2)}"',  # Keep the last one
        fixed
    )
    
    # Fix unclosed img tags (shouldn't happen but check)
    # Ensure all img tags are properly closed or self-closing
    fixed = re.sub(
        r'<img([^>]*)(?<!\/)>',
        r'<img\1 />',
        fixed
    )
    
    # Fix any broken image block structures
    # Ensure image blocks have proper closing
    fixed = re.sub(
        r'<!-- wp:image[^>]*>\s*<figure([^>]*)>',
        r'<!-- wp:image -->\n<figure\1>',
        fixed
    )
    
    return fixed

def main():
    console.print(Panel.fit(
        "[bold yellow]Fix Block Issues in Blog Posts[/bold yellow]",
        border_style="yellow"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    fixed_count = 0
    
    for post_id, title in BLOG_POSTS:
        console.print(f"\n[cyan]Checking: {title}[/cyan]")
        
        # Get post
        response = session.get(
            Config.get_api_url(f'posts/{post_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code != 200:
            console.print(f"  [red]✗ Error fetching post {post_id}[/red]")
            continue
        
        post = response.json()
        original_content = post.get('content', {}).get('raw', '')
        
        # Check for issues
        duplicate_styles = len(re.findall(r'style="[^"]*"\s+style="', original_content))
        
        if duplicate_styles > 0:
            console.print(f"  [yellow]⚠ Found {duplicate_styles} duplicate style attributes[/yellow]")
            
            # Fix content
            fixed_content = fix_content(original_content)
            
            # Verify fix worked
            remaining = len(re.findall(r'style="[^"]*"\s+style="', fixed_content))
            
            if remaining == 0:
                # Update post
                update_response = session.post(
                    Config.get_api_url(f'posts/{post_id}'),
                    json={'content': fixed_content},
                    timeout=30
                )
                
                if update_response.status_code == 200:
                    console.print(f"  [green]✓ Fixed {duplicate_styles} issues[/green]")
                    fixed_count += 1
                else:
                    console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
            else:
                console.print(f"  [red]✗ Fix incomplete, {remaining} issues remain[/red]")
        else:
            console.print(f"  [green]✓ No issues found[/green]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold green]Fixed {fixed_count} posts[/bold green]",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
