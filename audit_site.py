#!/usr/bin/env python3
"""
WordPress Site Audit Script
Analyzes existing pages, posts, categories, and structure
"""

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import Config
from modules.auth import WordPressAuth

console = Console()


def get_all_pages(session):
    """Get all published pages"""
    pages = []
    page = 1
    
    while True:
        response = session.get(
            Config.get_api_url('pages'),
            params={'per_page': 100, 'page': page, 'status': 'publish'},
            timeout=30
        )
        
        if response.status_code != 200:
            break
        
        data = response.json()
        if not data:
            break
        
        pages.extend(data)
        page += 1
    
    return pages


def get_all_posts(session):
    """Get all published posts"""
    posts = []
    page = 1
    
    while True:
        response = session.get(
            Config.get_api_url('posts'),
            params={'per_page': 100, 'page': page, 'status': 'publish'},
            timeout=30
        )
        
        if response.status_code != 200:
            break
        
        data = response.json()
        if not data:
            break
        
        posts.extend(data)
        page += 1
    
    return posts


def get_categories(session):
    """Get all categories"""
    response = session.get(
        Config.get_api_url('categories'),
        params={'per_page': 100},
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    return []


def get_tags(session):
    """Get all tags"""
    response = session.get(
        Config.get_api_url('tags'),
        params={'per_page': 100},
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    return []


def analyze_site(auth):
    """Analyze entire WordPress site"""
    console.print(Panel.fit(
        "[bold cyan]WordPress Site Audit[/bold cyan]\n"
        "[dim]Analyzing existing content structure[/dim]",
        border_style="cyan"
    ))
    
    session = auth.get_session()
    
    # Get all content
    console.print("\n[bold]Fetching content...[/bold]")
    pages = get_all_pages(session)
    posts = get_all_posts(session)
    categories = get_categories(session)
    tags = get_tags(session)
    
    console.print(f"[green]✓ Found {len(pages)} pages[/green]")
    console.print(f"[green]✓ Found {len(posts)} posts[/green]")
    console.print(f"[green]✓ Found {len(categories)} categories[/green]")
    console.print(f"[green]✓ Found {len(tags)} tags[/green]")
    
    # Pages table
    if pages:
        console.print("\n[bold cyan]━━━ EXISTING PAGES ━━━[/bold cyan]")
        pages_table = Table(show_header=True)
        pages_table.add_column("Title", style="cyan")
        pages_table.add_column("Slug", style="yellow")
        pages_table.add_column("URL", style="dim")
        
        for page in pages[:20]:  # Limit to first 20
            pages_table.add_row(
                page.get('title', {}).get('rendered', 'Untitled')[:40],
                page.get('slug', 'N/A')[:30],
                page.get('link', 'N/A')[:60]
            )
        
        console.print(pages_table)
        if len(pages) > 20:
            console.print(f"[dim]... and {len(pages) - 20} more pages[/dim]")
    
    # Posts table
    if posts:
        console.print("\n[bold cyan]━━━ EXISTING BLOG POSTS ━━━[/bold cyan]")
        posts_table = Table(show_header=True)
        posts_table.add_column("Title", style="cyan")
        posts_table.add_column("Slug", style="yellow")
        posts_table.add_column("Date", style="dim")
        
        for post in posts[:20]:  # Limit to first 20
            posts_table.add_row(
                post.get('title', {}).get('rendered', 'Untitled')[:40],
                post.get('slug', 'N/A')[:30],
                post.get('date', 'N/A')[:10]
            )
        
        console.print(posts_table)
        if len(posts) > 20:
            console.print(f"[dim]... and {len(posts) - 20} more posts[/dim]")
    
    # Categories table
    if categories:
        console.print("\n[bold cyan]━━━ CATEGORIES ━━━[/bold cyan]")
        cat_table = Table(show_header=True)
        cat_table.add_column("Name", style="cyan")
        cat_table.add_column("Slug", style="yellow")
        cat_table.add_column("Count", justify="right", style="green")
        
        for cat in categories[:15]:
            cat_table.add_row(
                cat.get('name', 'Unnamed'),
                cat.get('slug', 'N/A'),
                str(cat.get('count', 0))
            )
        
        console.print(cat_table)
    
    # Tags table
    if tags:
        console.print("\n[bold cyan]━━━ TAGS ━━━[/bold cyan]")
        tag_table = Table(show_header=True)
        tag_table.add_column("Name", style="cyan")
        tag_table.add_column("Slug", style="yellow")
        tag_table.add_column("Count", justify="right", style="green")
        
        for tag in tags[:15]:
            tag_table.add_row(
                tag.get('name', 'Unnamed'),
                tag.get('slug', 'N/A'),
                str(tag.get('count', 0))
            )
        
        console.print(tag_table)
        if len(tags) > 15:
            console.print(f"[dim]... and {len(tags) - 15} more tags[/dim]")
    
    # Save detailed report
    report = {
        'summary': {
            'total_pages': len(pages),
            'total_posts': len(posts),
            'total_categories': len(categories),
            'total_tags': len(tags)
        },
        'pages': [
            {
                'id': p.get('id'),
                'title': p.get('title', {}).get('rendered'),
                'slug': p.get('slug'),
                'link': p.get('link'),
                'parent': p.get('parent')
            } for p in pages
        ],
        'posts': [
            {
                'id': p.get('id'),
                'title': p.get('title', {}).get('rendered'),
                'slug': p.get('slug'),
                'link': p.get('link'),
                'date': p.get('date'),
                'categories': p.get('categories'),
                'tags': p.get('tags')
            } for p in posts
        ],
        'categories': [
            {
                'id': c.get('id'),
                'name': c.get('name'),
                'slug': c.get('slug'),
                'count': c.get('count')
            } for c in categories
        ],
        'tags': [
            {
                'id': t.get('id'),
                'name': t.get('name'),
                'slug': t.get('slug'),
                'count': t.get('count')
            } for t in tags
        ]
    }
    
    # Save to file
    with open('site_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    console.print(f"\n[green]✓ Detailed report saved to: site_audit_report.json[/green]")
    
    # Summary
    console.print("\n" + "="*60)
    console.print("\n[bold green]📊 Site Structure Summary[/bold green]\n")
    
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Item", style="cyan")
    summary_table.add_column("Count", justify="right", style="green bold")
    
    summary_table.add_row("Total Pages", str(len(pages)))
    summary_table.add_row("Total Posts", str(len(posts)))
    summary_table.add_row("Categories", str(len(categories)))
    summary_table.add_row("Tags", str(len(tags)))
    
    console.print(summary_table)
    console.print("\n" + "="*60 + "\n")


def main():
    try:
        Config.validate()
        
        auth = WordPressAuth()
        success, message, data = auth.test_connection()
        
        if not success:
            console.print(f"[red]❌ Connection failed: {message}[/red]")
            return
        
        analyze_site(auth)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
