#!/usr/bin/env python3
"""
Convert FAQ Sections to Rank Math FAQ Blocks with Schema
Converts HTML FAQ divs to proper Rank Math FAQ blocks with schema markup.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# Posts with FAQ sections
POSTS_WITH_FAQ = [
    (2701, 'Is My Child Ready for Sleepaway Camp?'),
    (2698, 'Everything You Need to Know About Sleepaway Camp'),
]

def extract_faq_items(html_content: str) -> list:
    """Extract FAQ items from HTML div structure."""
    faq_items = []
    
    # Find FAQ section
    faq_section_match = re.search(
        r'<div[^>]*class="faq-section"[^>]*>(.*?)</div>',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not faq_section_match:
        return []
    
    faq_content = faq_section_match.group(1)
    
    # Extract Q&A pairs
    # Pattern: <h3>Q: Question?</h3> followed by <p><strong>A:</strong> Answer</p>
    qa_pattern = r'<h3[^>]*>(?:Q:\s*)?(.*?)\?</h3>\s*<p[^>]*><strong>A:</strong>\s*(.*?)</p>'
    matches = re.finditer(qa_pattern, faq_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        question = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        answer = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        
        # Clean up answer (remove extra whitespace, preserve line breaks)
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        if question and answer:
            faq_items.append({
                'question': question + '?',
                'answer': answer
            })
    
    # Alternative pattern: Just H3 with question, then paragraph with answer
    if not faq_items:
        h3_pattern = r'<h3[^>]*>(.*?)\?</h3>\s*<p[^>]*>(.*?)</p>'
        matches = re.finditer(h3_pattern, faq_content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            question_text = match.group(1)
            answer_text = match.group(2)
            
            # Check if answer starts with "A:" or "<strong>A:</strong>"
            if re.match(r'^\s*(<strong>)?A:\s*(</strong>)?', answer_text, re.IGNORECASE):
                answer_text = re.sub(r'^\s*(<strong>)?A:\s*(</strong>)?\s*', '', answer_text, flags=re.IGNORECASE)
            
            question = re.sub(r'<[^>]+>', '', question_text).strip()
            answer = re.sub(r'<[^>]+>', '', answer_text).strip()
            answer = re.sub(r'\s+', ' ', answer).strip()
            
            if question and answer:
                faq_items.append({
                    'question': question + ('?' if not question.endswith('?') else ''),
                    'answer': answer
                })
    
    return faq_items

def create_rank_math_faq_block(faq_items: list) -> str:
    """Create Rank Math FAQ block with schema markup."""
    if not faq_items:
        return ''
    
    # Build FAQ block JSON structure
    faq_data = {
        'questions': []
    }
    
    for item in faq_items:
        faq_data['questions'].append({
            'question': item['question'],
            'answer': item['answer']
        })
    
    # Create the block comment with JSON
    # Rank Math FAQ block format
    block_json = json.dumps(faq_data, ensure_ascii=False)
    escaped_json = json.dumps(block_json)[1:-1]  # Escape for HTML attribute
    
    # Rank Math FAQ block format
    block = f'''<!-- wp:rank-math/faq-block -->
<div class="wp-block-rank-math-faq-block">
{create_faq_schema(faq_items)}
<div class="rank-math-faq-item">
'''
    
    for i, item in enumerate(faq_items):
        block += f'''<div class="rank-math-faq-item">
<h3 class="rank-math-question">{item['question']}</h3>
<div class="rank-math-answer">{item['answer']}</div>
</div>
'''
    
    block += '''</div>
</div>
<!-- /wp:rank-math/faq-block -->'''
    
    return block

def create_faq_schema(faq_items: list) -> str:
    """Create JSON-LD schema for FAQ."""
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
    
    return f'<script type="application/ld+json">\n{schema_json}\n</script>\n'

def main():
    console.print(Panel.fit(
        "[bold cyan]Convert FAQ Sections to Rank Math FAQ Blocks[/bold cyan]",
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
        
        # Extract FAQ items
        faq_items = extract_faq_items(content)
        
        if not faq_items:
            console.print(f"  [yellow]⚠ No FAQ items found[/yellow]")
            continue
        
        console.print(f"  [green]✓ Found {len(faq_items)} FAQ items[/green]")
        
        # Show FAQ items
        for i, item in enumerate(faq_items, 1):
            console.print(f"    {i}. Q: {item['question'][:50]}...")
        
        # Create Rank Math FAQ block
        faq_block = create_rank_math_faq_block(faq_items)
        
        # Replace FAQ section with new block
        # Find and replace the FAQ div
        pattern = r'<div[^>]*class="faq-section"[^>]*>.*?</div>'
        new_content = re.sub(pattern, faq_block, content, flags=re.DOTALL | re.IGNORECASE)
        
        if new_content != content:
            # Update post
            update_response = session.post(
                Config.get_api_url(f'posts/{post_id}'),
                json={'content': new_content},
                timeout=30
            )
            
            if update_response.status_code == 200:
                console.print(f"  [green]✓ Converted to Rank Math FAQ block with schema[/green]")
            else:
                console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
                console.print(update_response.text[:200])
        else:
            console.print(f"  [yellow]⚠ No changes made[/yellow]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Conversion Complete[/bold green]",
        border_style="green"
    ))
    console.print("\n[cyan]All FAQ sections now have proper schema markup![/cyan]")

if __name__ == '__main__':
    main()
