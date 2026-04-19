#!/usr/bin/env python3
"""
Fix Blog Post Issues:
1. Change image alignment from left to full-width (no wrapping)
2. Fix FAQ sections to ensure they render properly
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

BLOG_POSTS = [
    (2701, 'Is My Child Ready for Sleepaway Camp?'),
    (2697, 'How Camp Counselors Support First-Time Campers'),
    (2698, 'Everything You Need to Know About Sleepaway Camp'),
    (2699, 'Sleepaway Camp Safety: What Parents Should Know'),
    (2700, 'Rookie Day at Camp Lakota'),
    (2693, 'Packing for Sleepaway Camp'),
]

def fix_image_alignment(content: str) -> str:
    """Change images from left-aligned to full-width (no wrapping)."""
    fixed = content
    
    # Fix WordPress image blocks - remove left alignment
    # Pattern: <!-- wp:image {"align":"left",...} -->
    fixed = re.sub(
        r'<!-- wp:image \{"align":"left"',
        '<!-- wp:image {"align":"full"',
        fixed
    )
    
    # Fix figure alignment classes
    fixed = re.sub(
        r'<figure class="wp-block-image alignleft"',
        '<figure class="wp-block-image alignfull"',
        fixed
    )
    
    # Remove margin-right from images (causes wrapping)
    fixed = re.sub(
        r'style="([^"]*?)margin-right:[^;"]+;?([^"]*?)"',
        r'style="\1\2"',
        fixed
    )
    
    # Ensure images are full width
    fixed = re.sub(
        r'style="([^"]*?)width:600px([^"]*?)"',
        r'style="\1width:100%; max-width:100%\2"',
        fixed
    )
    
    # Add clearfix after images to prevent wrapping
    # Insert clear div after each image block
    def add_clearfix_after_image(match):
        image_block = match.group(0)
        # Check if there's already a clearfix
        if 'clearfix' not in image_block:
            return image_block + '\n<div style="clear: both;"></div>'
        return image_block
    
    fixed = re.sub(
        r'<!-- wp:image.*?<!-- /wp:image -->',
        add_clearfix_after_image,
        fixed,
        flags=re.DOTALL
    )
    
    return fixed

def fix_faq_section(content: str) -> str:
    """Ensure FAQ sections render properly with visible HTML."""
    fixed = content
    
    # Check if Rank Math FAQ block exists
    if 'wp:rank-math/faq-block' not in content:
        return fixed
    
    # Find FAQ block
    faq_pattern = r'(<!-- wp:rank-math/faq-block -->.*?<!-- /wp:rank-math/faq-block -->)'
    faq_match = re.search(faq_pattern, content, re.DOTALL)
    
    if not faq_match:
        return fixed
    
    faq_block = faq_match.group(1)
    
    # Check if it has proper HTML structure
    if '<h3' not in faq_block and '<div class="rank-math' not in faq_block:
        # Need to rebuild the FAQ block with proper HTML
        # Extract schema to get questions
        schema_match = re.search(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
            faq_block,
            re.DOTALL
        )
        
        if schema_match:
            try:
                schema_json = json.loads(schema_match.group(1))
                if schema_json.get('@type') == 'FAQPage' and 'mainEntity' in schema_json:
                    # Rebuild FAQ block with proper HTML
                    new_faq_block = '<!-- wp:rank-math/faq-block -->\n'
                    new_faq_block += '<div class="wp-block-rank-math-faq-block">\n'
                    new_faq_block += schema_match.group(0) + '\n'  # Keep schema
                    new_faq_block += '<div class="rank-math-faq-item">\n'
                    
                    for item in schema_json['mainEntity']:
                        question = item.get('name', '')
                        answer = item.get('acceptedAnswer', {}).get('text', '')
                        
                        new_faq_block += f'''<div class="rank-math-faq-item">
<h3 class="rank-math-question">{question}</h3>
<div class="rank-math-answer"><p>{answer}</p></div>
</div>
'''
                    
                    new_faq_block += '</div>\n</div>\n'
                    new_faq_block += '<!-- /wp:rank-math/faq-block -->'
                    
                    # Replace old block with new one
                    fixed = content.replace(faq_block, new_faq_block)
            except json.JSONDecodeError:
                console.print("  [yellow]⚠ Could not parse FAQ schema[/yellow]")
    
    return fixed

def main():
    console.print(Panel.fit(
        "[bold yellow]Fix Blog Post Issues[/bold yellow]",
        border_style="yellow"
    ))
    console.print("\n[cyan]Fixing:[/cyan]")
    console.print("  1. Image alignment (remove wrapping)")
    console.print("  2. FAQ section visibility\n")
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    fixed_count = 0
    
    for post_id, title in BLOG_POSTS:
        console.print(f"[cyan]Processing: {title}[/cyan]")
        
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
        
        # Fix image alignment
        content = fix_image_alignment(original_content)
        
        # Fix FAQ sections
        content = fix_faq_section(content)
        
        # Update if changed
        if content != original_content:
            update_response = session.post(
                Config.get_api_url(f'posts/{post_id}'),
                json={'content': content},
                timeout=30
            )
            
            if update_response.status_code == 200:
                console.print(f"  [green]✓ Fixed image alignment and FAQ[/green]")
                fixed_count += 1
            else:
                console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
        else:
            console.print(f"  [yellow]⚠ No changes needed[/yellow]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold green]Fixed {fixed_count} posts[/bold green]",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
