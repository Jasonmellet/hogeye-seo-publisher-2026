#!/usr/bin/env python3
"""
Fix FAQ Section for "Everything You Need to Know" Post
Ensures FAQ section is visible and properly formatted.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

POST_ID = 2698

def extract_faq_from_content(content: str) -> list:
    """Extract FAQ items from content."""
    faq_items = []
    
    # Look for FAQ section
    faq_match = re.search(
        r'<h2[^>]*>Frequently Asked Questions</h2>(.*?)(?=<h2|<h3[^>]*>Ready|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not faq_match:
        return []
    
    faq_content = faq_match.group(1)
    
    # Extract Q&A pairs
    # Pattern: <h3>Q: Question?</h3> followed by <p><strong>A:</strong> Answer</p>
    qa_pattern = r'<h3[^>]*>(?:Q:\s*)?(.*?)\?</h3>\s*<p[^>]*><strong>A:</strong>\s*(.*?)</p>'
    matches = re.finditer(qa_pattern, faq_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        question = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        answer = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        if question and answer:
            faq_items.append({
                'question': question + '?',
                'answer': answer
            })
    
    # Alternative: just H3 followed by paragraph
    if not faq_items:
        h3_pattern = r'<h3[^>]*>(.*?)\?</h3>\s*<p[^>]*>(.*?)</p>'
        matches = re.finditer(h3_pattern, faq_content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            question_text = match.group(1)
            answer_text = match.group(2)
            
            # Remove Q: prefix if present
            question_text = re.sub(r'^Q:\s*', '', question_text, flags=re.IGNORECASE)
            
            # Remove A: prefix if present
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

def create_visible_faq_section(faq_items: list) -> str:
    """Create visible FAQ section."""
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
    
    # Create simple, visible FAQ section
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
        "[bold cyan]Fix FAQ Section - Everything You Need to Know[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get post
    response = session.get(
        Config.get_api_url(f'posts/{POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]✗ Error fetching post {POST_ID}[/red]")
        return
    
    post = response.json()
    content = post.get('content', {}).get('raw', '')
    
    # Extract FAQ items
    faq_items = extract_faq_from_content(content)
    
    if not faq_items:
        console.print("[red]✗ No FAQ items found in content[/red]")
        return
    
    console.print(f"[green]✓ Found {len(faq_items)} FAQ items[/green]\n")
    
    # Show first few
    for i, item in enumerate(faq_items[:5], 1):
        console.print(f"  {i}. {item['question'][:60]}...")
    if len(faq_items) > 5:
        console.print(f"  ... and {len(faq_items) - 5} more\n")
    
    # Create new FAQ section
    new_faq_block = create_visible_faq_section(faq_items)
    
    # Remove old FAQ section (any format)
    # Pattern 1: H2 FAQ heading and everything until next H2 or Ready section
    content = re.sub(
        r'<h2[^>]*>Frequently Asked Questions</h2>.*?(?=<h2|<h3[^>]*>Ready|$)',
        new_faq_block,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Remove any div.faq-section wrappers that might hide content
    content = re.sub(
        r'<div[^>]*class="faq-section"[^>]*>',
        '',
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'</div>\s*<!--\s*end\s+faq-section\s*-->',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Update post
    update_response = session.post(
        Config.get_api_url(f'posts/{POST_ID}'),
        json={'content': content},
        timeout=30
    )
    
    if update_response.status_code == 200:
        console.print(f"\n[green]✓ FAQ section rebuilt and updated[/green]")
        console.print(f"[cyan]FAQ section should now be visible with {len(faq_items)} questions[/cyan]")
    else:
        console.print(f"\n[red]✗ Error updating: {update_response.status_code}[/red]")
        console.print(update_response.text[:200])

if __name__ == '__main__':
    main()
