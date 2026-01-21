#!/usr/bin/env python3
"""
Fix FAQ Blocks to Be Visible on Frontend
Uses a simpler, more compatible HTML structure that will definitely render.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

POSTS_WITH_FAQ = [
    (2701, 'Is My Child Ready for Sleepaway Camp?'),
    (2698, 'Everything You Need to Know About Sleepaway Camp'),
]

def extract_faq_from_schema(content: str) -> list:
    """Extract FAQ items from existing schema markup."""
    faq_items = []
    
    # Find schema script
    schema_match = re.search(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        content,
        re.DOTALL
    )
    
    if schema_match:
        try:
            schema_json = json.loads(schema_match.group(1))
            if schema_json.get('@type') == 'FAQPage' and 'mainEntity' in schema_json:
                for item in schema_json['mainEntity']:
                    question = item.get('name', '')
                    answer = item.get('acceptedAnswer', {}).get('text', '')
                    if question and answer:
                        faq_items.append({
                            'question': question,
                            'answer': answer
                        })
        except json.JSONDecodeError:
            pass
    
    return faq_items

def create_visible_faq_block(faq_items: list) -> str:
    """Create FAQ block with visible HTML that will definitely render."""
    if not faq_items:
        return ''
    
    # Create schema
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for item in faq_items:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": item['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item['answer']
            }
        })
    
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    
    # Create a simple, visible FAQ structure
    # Use Rank Math block but with standard HTML that will render
    block = '<!-- wp:rank-math/faq-block -->\n'
    block += '<div class="wp-block-rank-math-faq-block rank-math-faq-block">\n'
    block += f'<script type="application/ld+json">\n{schema_json}\n</script>\n'
    
    # Add FAQ items with clear, visible HTML
    for item in faq_items:
        block += f'''<div class="rank-math-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<h3 class="rank-math-question" itemprop="name" style="margin-top: 2rem; margin-bottom: 1rem; font-weight: bold;">{item['question']}</h3>
<div class="rank-math-answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer" style="margin-bottom: 1.5rem;">
<p itemprop="text" style="margin-bottom: 1.5rem; line-height: 1.7;">{item['answer']}</p>
</div>
</div>
'''
    
    block += '</div>\n'
    block += '<!-- /wp:rank-math/faq-block -->'
    
    return block

def main():
    console.print(Panel.fit(
        "[bold yellow]Fix FAQ Blocks - Make Visible on Frontend[/bold yellow]",
        border_style="yellow"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    for post_id, title in POSTS_WITH_FAQ:
        console.print(f"\n[cyan]Processing: {title}[/cyan]")
        
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
        content = post.get('content', {}).get('raw', '')
        
        # Extract FAQ items from existing schema
        faq_items = extract_faq_from_schema(content)
        
        if not faq_items:
            console.print(f"  [yellow]⚠ No FAQ items found[/yellow]")
            continue
        
        console.print(f"  [green]✓ Found {len(faq_items)} FAQ items[/green]")
        
        # Create visible FAQ block
        new_faq_block = create_visible_faq_block(faq_items)
        
        # Replace existing FAQ block
        pattern = r'<!-- wp:rank-math/faq-block.*?<!-- /wp:rank-math/faq-block -->'
        new_content = re.sub(pattern, new_faq_block, content, flags=re.DOTALL)
        
        if new_content != content:
            # Update post
            update_response = session.post(
                Config.get_api_url(f'posts/{post_id}'),
                json={'content': new_content},
                timeout=30
            )
            
            if update_response.status_code == 200:
                console.print(f"  [green]✓ Rebuilt FAQ block with visible structure[/green]")
                console.print(f"  [cyan]FAQ questions should now be visible on frontend[/cyan]")
            else:
                console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
                console.print(update_response.text[:200])
        else:
            console.print(f"  [yellow]⚠ No changes made[/yellow]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Blocks Updated[/bold green]",
        border_style="green"
    ))
    console.print("\n[cyan]FAQ sections should now be visible with proper styling![/cyan]")

if __name__ == '__main__':
    main()
