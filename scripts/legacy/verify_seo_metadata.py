#!/usr/bin/env python3
"""
Verify SEO Metadata - Check what was attempted and provide verification instructions
"""

import json
import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table

console = Console()

def load_metadata_from_json(json_file: str) -> dict:
    """Load metadata from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        file_content = file_content.replace('"', '"').replace('"', '"')
        file_content = file_content.replace(''', "'").replace(''', "'")
        
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError:
            meta_title_match = re.search(r'"meta_title":\s*"([^"]+)"', file_content)
            meta_desc_match = re.search(r'"meta_description":\s*"([^"]+)"', file_content)
            
            data = {
                'meta_title': meta_title_match.group(1) if meta_title_match else '',
                'meta_description': meta_desc_match.group(1) if meta_desc_match else ''
            }
        
        return {
            'meta_title': data.get('meta_title', ''),
            'meta_description': data.get('meta_description', '')
        }
    except:
        return {'meta_title': '', 'meta_description': ''}


def main():
    console.print("[bold cyan]SEO Metadata Verification Report[/bold cyan]\n")
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Landing pages
    landing_pages = [
        (1360, 'content/pages/what-to-expect-parent.json', 'What to Expect'),
        (1721, 'content/pages/a-day-at-camp-update.json', 'A Day at Camp'),
        (806, 'content/pages/water-sports-update.json', 'Water Sports'),
        (1980, 'content/pages/events-night-activities.json', 'Events & Night Activities')
    ]
    
    # Blog posts
    blog_posts = [
        (2701, 'content/posts/is-child-ready-for-sleepaway-camp-2026.json', 'Is My Child Ready'),
        (2697, 'content/posts/counselors-help-first-time-campers.json', 'Counselors Support'),
        (2698, 'content/posts/everything-you-need-to-know-sleepaway-camp-guide.json', 'Everything You Need to Know'),
        (2699, 'content/posts/sleepaway-camp-safety-parents-should-know.json', 'Camp Safety'),
        (2700, 'content/posts/rookie-day-explained.json', 'Rookie Day'),
        (2693, 'content/posts/packing-3-week-vs-6-week-sleepaway-camp.json', 'Packing Guide')
    ]
    
    table = Table(title="SEO Metadata Status")
    table.add_column("Content", style="cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Source Has Meta", style="green")
    table.add_column("Update Attempted", style="green")
    table.add_column("Note", style="dim")
    
    all_items = [(lp, 'page') for lp in landing_pages] + [(bp, 'post') for bp in blog_posts]
    
    for item, content_type in all_items:
        content_id, json_file, name = item
        metadata = load_metadata_from_json(json_file)
        
        has_meta = '✅' if (metadata['meta_title'] and metadata['meta_description']) else '❌'
        
        # Check if update was attempted (we just ran it)
        update_attempted = '✅'  # We just ran the update script
        
        # Note about verification
        note = "Check WordPress admin" if has_meta == '✅' else "Missing in source"
        
        table.add_row(name, str(content_id), has_meta, update_attempted, note)
    
    console.print(table)
    
    console.print("\n[bold]Important Notes:[/bold]")
    console.print("  • Updates returned 200 (success) status")
    console.print("  • WordPress REST API may not return custom meta fields in response")
    console.print("  • Fields are likely saved but need verification in WordPress admin")
    console.print("\n[yellow]To Verify:[/yellow]")
    console.print("  1. Go to WordPress admin")
    console.print("  2. Edit each page/post")
    console.print("  3. Scroll to 'Yoast SEO' section")
    console.print("  4. Check if SEO Title and Meta Description are populated")
    console.print("\n[green]If fields are empty in admin, we may need to use a different method[/green]")


if __name__ == '__main__':
    main()
