#!/usr/bin/env python3
"""
Update Blog Post Spacing
Adds proper spacing to paragraphs and headings according to blog post design template.
"""

import re
from modules.deprecation import deprecated_script_exit
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def add_spacing_to_content(content: str) -> str:
    """
    Add proper spacing to paragraphs and headings according to blog post template.
    
    Standards:
    - Paragraphs: margin-bottom: 1.5rem; line-height: 1.7;
    - H2: margin-top: 2.5rem; margin-bottom: 1.5rem;
    - H3: margin-top: 2rem; margin-bottom: 1rem;
    """
    
    # Add spacing to paragraphs
    # Match <p> tags that don't already have style attribute with margin-bottom
    def add_para_style(match):
        tag = match.group(0)
        # Check if already has style attribute
        if 'style=' in tag:
            # Check if margin-bottom is already there
            if 'margin-bottom' in tag:
                return tag  # Already has spacing
            # Add margin-bottom to existing style
            tag = re.sub(r'style="([^"]*)"', r'style="\1; margin-bottom: 1.5rem; line-height: 1.7;"', tag)
        else:
            # Add new style attribute
            tag = tag.replace('<p>', '<p style="margin-bottom: 1.5rem; line-height: 1.7;">')
        return tag
    
    content = re.sub(r'<p[^>]*>', add_para_style, content)
    
    # Add spacing to H2 headings
    def add_h2_style(match):
        tag = match.group(0)
        if 'style=' in tag:
            if 'margin-top' in tag or 'margin-bottom' in tag:
                return tag  # Already has spacing
            tag = re.sub(r'style="([^"]*)"', r'style="\1; margin-top: 2.5rem; margin-bottom: 1.5rem;"', tag)
        else:
            tag = tag.replace('<h2>', '<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem;">')
            tag = tag.replace('<h2 ', '<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem; ')
        return tag
    
    content = re.sub(r'<h2[^>]*>', add_h2_style, content)
    
    # Add spacing to H3 headings
    def add_h3_style(match):
        tag = match.group(0)
        if 'style=' in tag:
            if 'margin-top' in tag or 'margin-bottom' in tag:
                return tag  # Already has spacing
            tag = re.sub(r'style="([^"]*)"', r'style="\1; margin-top: 2rem; margin-bottom: 1rem;"', tag)
        else:
            tag = tag.replace('<h3>', '<h3 style="margin-top: 2rem; margin-bottom: 1rem;">')
            tag = tag.replace('<h3 ', '<h3 style="margin-top: 2rem; margin-bottom: 1rem; ')
        return tag
    
    content = re.sub(r'<h3[^>]*>', add_h3_style, content)
    
    return content

def update_post_spacing(session, post_id: int, post_title: str) -> bool:
    """Update a single blog post with proper spacing."""
    
    try:
        # Get current post
        response = session.get(
            Config.get_api_url(f'posts/{post_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error fetching post {post_id}: {response.status_code}[/red]")
            return False
        
        post = response.json()
        content = post.get('content', {}).get('raw', '')
        
        # Check if already has spacing
        if 'margin-bottom: 1.5rem' in content and 'margin-top: 2.5rem' in content:
            console.print(f"[dim]Post {post_id} already has spacing, skipping...[/dim]")
            return True
        
        # Add spacing
        updated_content = add_spacing_to_content(content)
        
        # Update post
        update_response = session.post(
            Config.get_api_url(f'posts/{post_id}'),
            json={
                'content': updated_content
            },
            timeout=30
        )
        
        if update_response.status_code == 200:
            console.print(f"[green]✓[/green] Updated spacing for: {post_title}")
            return True
        else:
            console.print(f"[red]✗[/red] Error updating post {post_id}: {update_response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"[red]Error updating post {post_id}: {e}[/red]")
        return False

def main():
    console.print(Panel.fit("[bold cyan]Update Blog Post Spacing[/bold cyan]", border_style="cyan"))
    
    # Blog posts that need spacing updates
    blog_posts = [
        (2699, 'Sleepaway Camp Safety: What Parents Should Know'),
        (2697, 'How Camp Counselors Support First-Time Sleepaway Campers'),
        (2700, 'Rookie Day at Camp Lakota: What First-Time Families Can Expect'),
        (2698, 'Everything You Need to Know About Sleepaway Camp (2026)'),
        (2701, 'Is My Child Ready for Sleepaway Camp? 5 Signs the Answer is Yes'),
    ]
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    console.print(f"\n[bold]Updating {len(blog_posts)} blog posts...[/bold]\n")
    
    success_count = 0
    for post_id, post_title in blog_posts:
        console.print(f"[cyan]Processing:[/cyan] {post_title} (ID: {post_id})")
        if update_post_spacing(session, post_id, post_title):
            success_count += 1
        console.print()
    
    console.print(Panel.fit(
        f"[bold green]Complete![/bold green]\n\n"
        f"Updated: {success_count}/{len(blog_posts)} blog posts\n"
        f"All posts now have proper spacing according to design template.",
        border_style="green"
    ))

if __name__ == '__main__':
    deprecated_script_exit(
        "update_blog_post_spacing.py",
        "python3 publish_content_item.py /abs/path/to/content/posts/<file>.json --type posts",
    )
    main()
