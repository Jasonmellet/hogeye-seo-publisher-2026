#!/usr/bin/env python3
"""
Remove Duplicate FAQ Sections
Cleans up duplicate FAQ sections and ensures only one visible FAQ section exists.
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
    
    # Find all schema scripts
    schema_matches = re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        content,
        re.DOTALL
    )
    
    for schema_match in schema_matches:
        try:
            schema_json = json.loads(schema_match.group(1))
            if schema_json.get('@type') == 'FAQPage' and 'mainEntity' in schema_json:
                for item in schema_json['mainEntity']:
                    question = item.get('name', '')
                    answer = item.get('acceptedAnswer', {}).get('text', '')
                    if question and answer:
                        # Avoid duplicates
                        if not any(q['question'] == question for q in faq_items):
                            faq_items.append({
                                'question': question,
                                'answer': answer
                            })
        except json.JSONDecodeError:
            pass
    
    return faq_items

def create_clean_faq_section(faq_items: list) -> str:
    """Create a single, clean FAQ section."""
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
    
    # Create single FAQ section
    block = '<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem;">Frequently Asked Questions</h2>\n\n'
    block += f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'
    
    for item in faq_items:
        block += f'''<div class="faq-item" style="margin-bottom: 2rem;">
<h3 style="margin-top: 2rem; margin-bottom: 1rem; font-weight: bold;">{item['question']}</h3>
<p style="margin-bottom: 1.5rem; line-height: 1.7;">{item['answer']}</p>
</div>

'''
    
    return block

def main():
    console.print(Panel.fit(
        "[bold yellow]Remove Duplicate FAQ Sections[/bold yellow]",
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
        
        # Extract all FAQ items
        faq_items = extract_faq_from_schema(content)
        
        if not faq_items:
            console.print(f"  [yellow]⚠ No FAQ items found[/yellow]")
            continue
        
        console.print(f"  [green]✓ Found {len(faq_items)} unique FAQ items[/green]")
        
        # Remove ALL FAQ sections (Rank Math blocks, duplicate H2s, etc.)
        # Pattern 1: Rank Math blocks
        content = re.sub(
            r'<!-- wp:rank-math/faq-block.*?<!-- /wp:rank-math/faq-block -->',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Pattern 2: FAQ sections with H2 "Frequently Asked Questions"
        # Find the first occurrence and everything until the next H2 or end
        faq_pattern = r'<h2[^>]*>Frequently Asked Questions</h2>.*?(?=<h2|<h3[^>]*>Ready|$)'
        faq_matches = list(re.finditer(faq_pattern, content, re.DOTALL | re.IGNORECASE))
        
        if faq_matches:
            console.print(f"  [yellow]⚠ Found {len(faq_matches)} FAQ sections, removing duplicates[/yellow]")
            # Remove all but keep track of where to insert
            for match in reversed(faq_matches):
                content = content[:match.start()] + content[match.end():]
        
        # Create clean FAQ section
        new_faq_block = create_clean_faq_section(faq_items)
        
        # Insert before "Ready to start" or at the end
        cta_pattern = r'(<h3[^>]*>Ready to start.*?</h3>)'
        cta_match = re.search(cta_pattern, content, re.IGNORECASE)
        
        if cta_match:
            insert_pos = cta_match.start()
            content = content[:insert_pos] + '\n\n' + new_faq_block + '\n\n' + content[insert_pos:]
        else:
            # Append at end
            content = content + '\n\n' + new_faq_block
        
        # Update post
        update_response = session.post(
            Config.get_api_url(f'posts/{post_id}'),
            json={'content': content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            console.print(f"  [green]✓ Removed duplicates and created single FAQ section[/green]")
        else:
            console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Sections Cleaned[/bold green]",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
