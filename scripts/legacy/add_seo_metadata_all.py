#!/usr/bin/env python3
"""
Add SEO metadata to all landing pages and blog posts
"""

import json
import re
import os
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_metadata_from_json(json_file: str) -> dict:
    """Load metadata from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Fix JSON issues
        file_content = file_content.replace('"', '"').replace('"', '"')
        file_content = file_content.replace(''', "'").replace(''', "'")
        
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError:
            # Extract manually
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
    except Exception as e:
        console.print(f"[red]Error loading {json_file}: {e}[/red]")
        return {'meta_title': '', 'meta_description': ''}


def update_page_seo(session, page_id: int, meta_title: str, meta_description: str) -> bool:
    """Update page SEO metadata"""
    try:
        update_data = {
            'meta': {
                '_yoast_wpseo_title': meta_title,
                '_yoast_wpseo_metadesc': meta_description,
            }
        }
        
        response = session.post(
            Config.get_api_url(f'pages/{page_id}'),
            json=update_data,
            timeout=30
        )
        
        return response.status_code == 200
    except Exception as e:
        console.print(f"[red]Error updating page {page_id}: {e}[/red]")
        return False


def update_post_seo(session, post_id: int, meta_title: str, meta_description: str) -> bool:
    """Update post SEO metadata"""
    try:
        update_data = {
            'meta': {
                '_yoast_wpseo_title': meta_title,
                '_yoast_wpseo_metadesc': meta_description,
            }
        }
        
        response = session.post(
            Config.get_api_url(f'posts/{post_id}'),
            json=update_data,
            timeout=30
        )
        
        return response.status_code == 200
    except Exception as e:
        console.print(f"[red]Error updating post {post_id}: {e}[/red]")
        return False


def main():
    console.print(Panel.fit("[bold cyan]Add SEO Metadata to All Pages & Posts[/bold cyan]"))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Landing pages mapping
    landing_pages = [
        (1360, 'content/pages/what-to-expect-parent.json', 'What to Expect'),
        (1721, 'content/pages/a-day-at-camp-update.json', 'A Day at Camp'),
        (806, 'content/pages/water-sports-update.json', 'Water Sports'),
        (1980, 'content/pages/events-night-activities.json', 'Events & Night Activities')
    ]
    
    # Blog posts mapping
    blog_posts = [
        (2701, 'content/posts/is-child-ready-for-sleepaway-camp-2026.json', 'Is My Child Ready'),
        (2697, 'content/posts/counselors-help-first-time-campers.json', 'Counselors Support'),
        (2698, 'content/posts/everything-you-need-to-know-sleepaway-camp-guide.json', 'Everything You Need to Know'),
        (2699, 'content/posts/sleepaway-camp-safety-parents-should-know.json', 'Camp Safety'),
        (2700, 'content/posts/rookie-day-explained.json', 'Rookie Day'),
        (2693, 'content/posts/packing-3-week-vs-6-week-sleepaway-camp.json', 'Packing Guide')
    ]
    
    results_table = Table(title="SEO Metadata Update Results")
    results_table.add_column("Content", style="cyan")
    results_table.add_column("ID", style="yellow")
    results_table.add_column("SEO Title", style="green")
    results_table.add_column("Meta Desc", style="green")
    results_table.add_column("Status", style="dim")
    
    # Update landing pages
    console.print("\n[bold]Updating Landing Pages...[/bold]\n")
    
    for page_id, json_file, name in landing_pages:
        metadata = load_metadata_from_json(json_file)
        
        if metadata['meta_title'] and metadata['meta_description']:
            success = update_page_seo(
                session,
                page_id,
                metadata['meta_title'],
                metadata['meta_description']
            )
            
            status = "✅ Updated" if success else "❌ Failed"
            results_table.add_row(
                name,
                str(page_id),
                "✅",
                "✅",
                status
            )
        else:
            results_table.add_row(
                name,
                str(page_id),
                "❌ Missing",
                "❌ Missing",
                "⚠️ No metadata in source"
            )
    
    # Update blog posts
    console.print("\n[bold]Updating Blog Posts...[/bold]\n")
    
    for post_id, json_file, name in blog_posts:
        metadata = load_metadata_from_json(json_file)
        
        if metadata['meta_title'] and metadata['meta_description']:
            success = update_post_seo(
                session,
                post_id,
                metadata['meta_title'],
                metadata['meta_description']
            )
            
            status = "✅ Updated" if success else "❌ Failed"
            results_table.add_row(
                name,
                str(post_id),
                "✅",
                "✅",
                status
            )
        else:
            results_table.add_row(
                name,
                str(post_id),
                "❌ Missing",
                "❌ Missing",
                "⚠️ No metadata in source"
            )
    
    console.print("\n")
    console.print(results_table)
    
    # Verify
    console.print("\n[bold]Verifying Updates...[/bold]\n")
    
    verify_table = Table(title="Verification")
    verify_table.add_column("Content", style="cyan")
    verify_table.add_column("ID", style="yellow")
    verify_table.add_column("Has SEO Title", style="green")
    verify_table.add_column("Has Meta Desc", style="green")
    
    all_pages = landing_pages + [(pid, '', name) for pid, _, name in blog_posts]
    
    for item in all_pages:
        content_id = item[0]
        name = item[2]
        
        # Determine if page or post
        is_page = any(content_id == pid for pid, _, _ in landing_pages)
        endpoint = 'pages' if is_page else 'posts'
        
        response = session.get(
            Config.get_api_url(f'{endpoint}/{content_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()
            meta = content.get('meta', {})
            has_title = '✅' if meta.get('_yoast_wpseo_title') else '❌'
            has_desc = '✅' if meta.get('_yoast_wpseo_metadesc') else '❌'
            
            verify_table.add_row(name, str(content_id), has_title, has_desc)
    
    console.print(verify_table)
    
    console.print("\n[bold green]✅ SEO Metadata Update Complete![/bold green]")


if __name__ == '__main__':
    main()
