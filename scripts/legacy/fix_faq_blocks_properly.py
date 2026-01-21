#!/usr/bin/env python3
"""
Fix FAQ Blocks to Use Proper Rank Math Format
Rebuilds FAQ blocks with correct HTML structure that Rank Math expects.
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

def create_proper_rank_math_faq_block(faq_items: list) -> str:
    """Create properly formatted Rank Math FAQ block."""
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
    
    # Build the FAQ block with proper Rank Math structure
    # Rank Math expects: wp-block-rank-math-faq-block wrapper
    # Each item should be: rank-math-faq-item with rank-math-question and rank-math-answer
    block = '<!-- wp:rank-math/faq-block -->\n'
    block += '<div class="wp-block-rank-math-faq-block">\n'
    block += f'<script type="application/ld+json">\n{schema_json}\n</script>\n'
    
    # Add FAQ items
    for item in faq_items:
        block += f'''<div class="rank-math-faq-item">
<h3 class="rank-math-question">{item['question']}</h3>
<div class="rank-math-answer"><p>{item['answer']}</p></div>
</div>
'''
    
    block += '</div>\n'
    block += '<!-- /wp:rank-math/faq-block -->'
    
    return block

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix FAQ Blocks - Proper Rank Math Format[/bold cyan]",
        border_style="cyan"
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
        
        # Create proper FAQ block
        new_faq_block = create_proper_rank_math_faq_block(faq_items)
        
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
                console.print(f"  [green]✓ Rebuilt FAQ block with proper structure[/green]")
            else:
                console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
        else:
            console.print(f"  [yellow]⚠ No changes made[/yellow]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Blocks Fixed[/bold green]",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
