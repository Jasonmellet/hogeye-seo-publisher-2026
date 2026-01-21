#!/usr/bin/env python3
"""
Update Post Metadata
Adds categories, tags, and SEO metadata to published posts
"""

import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Config
from modules.auth import WordPressAuth

console = Console()


def get_or_create_category(session, category_name):
    """Get category ID by name, create if doesn't exist"""
    try:
        # Search for existing category
        response = session.get(
            Config.get_api_url('categories'),
            params={'search': category_name, 'per_page': 100},
            timeout=30
        )
        
        if response.status_code == 200:
            categories = response.json()
            # Look for exact match
            for cat in categories:
                if cat['name'].lower() == category_name.lower():
                    console.print(f"  [dim]Found category: {category_name} (ID: {cat['id']})[/dim]")
                    return cat['id']
        
        # Category doesn't exist, create it
        console.print(f"  [yellow]Creating new category: {category_name}[/yellow]")
        response = session.post(
            Config.get_api_url('categories'),
            json={'name': category_name},
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            console.print(f"  [green]Created category: {category_name} (ID: {result['id']})[/green]")
            return result['id']
        else:
            console.print(f"  [red]Failed to create category: {response.text[:100]}[/red]")
            return None
    
    except Exception as e:
        console.print(f"  [red]Error with category '{category_name}': {e}[/red]")
        return None


def get_or_create_tag(session, tag_name):
    """Get tag ID by name, create if doesn't exist"""
    try:
        # Search for existing tag
        response = session.get(
            Config.get_api_url('tags'),
            params={'search': tag_name, 'per_page': 100},
            timeout=30
        )
        
        if response.status_code == 200:
            tags = response.json()
            # Look for exact match
            for tag in tags:
                if tag['name'].lower() == tag_name.lower():
                    return tag['id']
        
        # Tag doesn't exist, create it
        response = session.post(
            Config.get_api_url('tags'),
            json={'name': tag_name},
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            return result['id']
        else:
            return None
    
    except Exception as e:
        console.print(f"  [red]Error with tag '{tag_name}': {e}[/red]")
        return None


def find_post_by_slug(session, slug):
    """Find post ID by slug"""
    try:
        response = session.get(
            Config.get_api_url('posts'),
            params={'slug': slug, 'status': 'any'},
            timeout=30
        )
        
        if response.status_code == 200:
            posts = response.json()
            if posts and len(posts) > 0:
                return posts[0]['id']
        return None
    except Exception as e:
        console.print(f"  [red]Error finding post: {e}[/red]")
        return None


def update_post_metadata(session, post_id, category_ids, tag_ids, meta_title, meta_description):
    """Update post with metadata"""
    try:
        update_data = {
            'categories': category_ids,
            'tags': tag_ids,
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
        console.print(f"  [red]Error updating post: {e}[/red]")
        return False


def load_blog_posts():
    """Load all blog post JSON files"""
    posts_dir = Path('content/posts')
    
    if not posts_dir.exists():
        return []
    
    posts = []
    for json_file in posts_dir.glob('*.json'):
        # Skip example files
        if 'example' in json_file.name.lower():
            continue
        
        try:
            with open(json_file, 'r') as f:
                post_data = json.load(f)
                post_data['_source_file'] = json_file.name
                posts.append(post_data)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {json_file.name}: {e}[/yellow]")
    
    return posts


def main():
    """Main execution"""
    console.print(Panel.fit(
        "[bold cyan]Update Post Metadata[/bold cyan]\n"
        "[dim]Adding categories, tags, and SEO metadata[/dim]",
        border_style="cyan"
    ))
    
    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"\n[red]Configuration Error:[/red]\n{e}\n")
        sys.exit(1)
    
    # Test connection
    console.print("\n[bold]Testing WordPress connection...[/bold]")
    auth = WordPressAuth()
    success, message, data = auth.test_connection()
    
    if not success:
        console.print(f"[red]❌ Connection failed: {message}[/red]")
        sys.exit(1)
    
    console.print(f"[green]✅ Connected to: {data.get('site_name', 'WordPress')}[/green]")
    
    # Load blog posts
    console.print("\n[bold]Loading blog posts...[/bold]")
    posts = load_blog_posts()
    
    if not posts:
        console.print("[red]❌ No blog posts found[/red]")
        sys.exit(1)
    
    console.print(f"[green]✅ Found {len(posts)} blog post(s)[/green]")
    
    session = auth.get_session()
    
    # Track results
    results = {
        'success': [],
        'failed': [],
        'not_found': []
    }
    
    console.print("\n[bold]Processing posts...[/bold]\n")
    
    for idx, post_data in enumerate(posts, 1):
        title = post_data['title']
        slug = post_data.get('slug', '')
        
        console.print(f"[cyan]━━━ Post {idx}/{len(posts)} ━━━[/cyan]")
        console.print(f"[bold]{title}[/bold]")
        
        # Find the post
        console.print("  [dim]Finding post in WordPress...[/dim]")
        post_id = find_post_by_slug(session, slug)
        
        if not post_id:
            console.print(f"  [red]❌ Post not found with slug: {slug}[/red]")
            results['not_found'].append(title)
            continue
        
        console.print(f"  [green]Found post ID: {post_id}[/green]")
        
        # Process categories
        category_ids = []
        categories = post_data.get('categories', [])
        if categories:
            console.print(f"  [dim]Processing {len(categories)} category(ies)...[/dim]")
            for cat_name in categories:
                cat_id = get_or_create_category(session, cat_name)
                if cat_id:
                    category_ids.append(cat_id)
        
        # Process tags
        tag_ids = []
        tags = post_data.get('tags', [])
        if tags:
            console.print(f"  [dim]Processing {len(tags)} tag(s)...[/dim]")
            for tag_name in tags:
                tag_id = get_or_create_tag(session, tag_name)
                if tag_id:
                    tag_ids.append(tag_id)
        
        # Get SEO metadata
        meta_title = post_data.get('meta_title', '')
        meta_description = post_data.get('meta_description', '')
        
        console.print(f"  [dim]Updating metadata...[/dim]")
        console.print(f"    Categories: {len(category_ids)}")
        console.print(f"    Tags: {len(tag_ids)}")
        console.print(f"    SEO Title: {meta_title[:50]}..." if len(meta_title) > 50 else f"    SEO Title: {meta_title}")
        console.print(f"    SEO Description: {meta_description[:50]}..." if len(meta_description) > 50 else f"    SEO Description: {meta_description}")
        
        # Update the post
        success = update_post_metadata(
            session,
            post_id,
            category_ids,
            tag_ids,
            meta_title,
            meta_description
        )
        
        if success:
            console.print(f"  [green]✅ Metadata updated successfully![/green]\n")
            results['success'].append(title)
        else:
            console.print(f"  [red]❌ Failed to update metadata[/red]\n")
            results['failed'].append(title)
    
    # Print summary
    console.print("\n" + "━" * 60)
    console.print("\n[bold green]📊 Update Summary[/bold green]\n")
    
    summary_table = Table(show_header=True, header_style="bold cyan")
    summary_table.add_column("Result", style="cyan")
    summary_table.add_column("Count", justify="right", style="green")
    
    summary_table.add_row("✅ Updated Successfully", str(len(results['success'])))
    summary_table.add_row("❌ Failed", str(len(results['failed'])))
    summary_table.add_row("⚠️  Not Found", str(len(results['not_found'])))
    summary_table.add_row("━" * 20, "━" * 5)
    summary_table.add_row("Total", str(len(posts)))
    
    console.print(summary_table)
    
    if results['success']:
        console.print("\n[bold green]✅ Successfully Updated:[/bold green]")
        for title in results['success']:
            console.print(f"  • {title}")
    
    if results['failed']:
        console.print("\n[bold red]❌ Failed:[/bold red]")
        for title in results['failed']:
            console.print(f"  • {title}")
    
    if results['not_found']:
        console.print("\n[bold yellow]⚠️  Not Found in WordPress:[/bold yellow]")
        for title in results['not_found']:
            console.print(f"  • {title}")
    
    console.print("\n[bold]📝 Next Steps:[/bold]")
    console.print("  1. Check posts in WordPress admin")
    console.print("  2. Verify categories and tags are assigned")
    console.print("  3. Check Yoast SEO panel for meta title/description")
    console.print("  4. If SEO fields are empty, you may need to:")
    console.print("     - Install Yoast SEO plugin (or similar)")
    console.print("     - Or manually add meta in WordPress admin")
    
    console.print("\n" + "━" * 60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Update cancelled[/yellow]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
