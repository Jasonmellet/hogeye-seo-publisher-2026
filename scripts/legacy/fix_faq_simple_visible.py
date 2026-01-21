#!/usr/bin/env python3
"""
Fix FAQ Sections - Use Simple Visible HTML
Replaces Rank Math blocks with simple HTML that will definitely render,
while keeping schema markup for SEO.
"""

import re
import json
from modules.deprecation import deprecated_script_exit
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

def create_simple_visible_faq(faq_items: list) -> str:
    """Create simple, visible FAQ HTML that will definitely render."""
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
    
    # Create simple HTML FAQ section that will definitely render
    # Use standard H3 headings and paragraphs - no special classes needed
    block = '<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem;">Frequently Asked Questions</h2>\n\n'
    
    # Add schema in a script tag (for SEO, but won't affect display)
    block += f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'
    
    # Add FAQ items as simple HTML
    for item in faq_items:
        block += f'''<div class="faq-item" style="margin-bottom: 2rem;">
<h3 style="margin-top: 2rem; margin-bottom: 1rem; font-weight: bold;">{item['question']}</h3>
<p style="margin-bottom: 1.5rem; line-height: 1.7;">{item['answer']}</p>
</div>

'''
    
    return block

def main():
    console.print(Panel.fit(
        "[bold cyan]Fix FAQ Sections - Simple Visible HTML[/bold cyan]",
        border_style="cyan"
    ))
    console.print("\n[yellow]Using simple H2/H3 structure that will definitely render[/yellow]\n")
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    for post_id, title in POSTS_WITH_FAQ:
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
        content = post.get('content', {}).get('raw', '')
        
        # Extract FAQ items from existing schema
        faq_items = extract_faq_from_schema(content)
        
        if not faq_items:
            console.print(f"  [yellow]⚠ No FAQ items found[/yellow]")
            continue
        
        console.print(f"  [green]✓ Found {len(faq_items)} FAQ items[/green]")
        
        # Create simple visible FAQ
        new_faq_block = create_simple_visible_faq(faq_items)
        
        # Replace existing FAQ block (Rank Math or any other format)
        # Try multiple patterns
        patterns = [
            r'<!-- wp:rank-math/faq-block.*?<!-- /wp:rank-math/faq-block -->',
            r'<h2[^>]*>Frequently Asked Questions</h2>.*?(?=<h2|</div>|$)',
        ]
        
        new_content = content
        for pattern in patterns:
            new_content = re.sub(pattern, new_faq_block, new_content, flags=re.DOTALL | re.IGNORECASE)
        
        # If no FAQ section found, add it before the final CTA
        if new_content == content:
            # Find "Ready to start" or similar CTA section
            cta_pattern = r'(<h3[^>]*>Ready to start.*?</h3>)'
            cta_match = re.search(cta_pattern, new_content, re.IGNORECASE)
            if cta_match:
                insert_pos = cta_match.start()
                new_content = new_content[:insert_pos] + '\n\n' + new_faq_block + '\n\n' + new_content[insert_pos:]
            else:
                # Just append at the end
                new_content = new_content + '\n\n' + new_faq_block
        
        if new_content != content:
            # Update post
            update_response = session.post(
                Config.get_api_url(f'posts/{post_id}'),
                json={'content': new_content},
                timeout=30
            )
            
            if update_response.status_code == 200:
                console.print(f"  [green]✓ Created simple visible FAQ section[/green]")
                console.print(f"  [cyan]FAQ questions will now display as H3 headings[/cyan]")
            else:
                console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
        else:
            console.print(f"  [yellow]⚠ No changes made[/yellow]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Sections Fixed[/bold green]",
        border_style="green"
    ))
    console.print("\n[cyan]FAQ sections now use simple H2/H3 HTML that will definitely render![/cyan]")
    console.print("[cyan]Schema markup is preserved for SEO.[/cyan]")

if __name__ == '__main__':
    deprecated_script_exit(
        "fix_faq_simple_visible.py",
        "python3 publish_content_item.py /abs/path/to/content/posts/<file>.json --type posts",
    )
    main()
