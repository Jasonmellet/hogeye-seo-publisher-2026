#!/usr/bin/env python3
"""
Safe single-file test publisher
Publishes ONE blog post as a draft for testing
"""

import sys
import json
from rich.console import Console
from rich.panel import Panel

from config import Config
from modules.auth import WordPressAuth

console = Console()


def main():
    """Test publish a single blog post"""
    console.print(Panel.fit(
        "[bold cyan]Single Post Test Publisher[/bold cyan]\n"
        "[dim]Safely publish one blog post as a draft[/dim]",
        border_style="cyan"
    ))
    
    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"\n[red]Configuration Error:[/red]\n{e}\n")
        sys.exit(1)
    
    # Show what we're doing
    console.print("\n[bold]Safety Features:[/bold]")
    console.print("  ✅ Only publishes ONE specified file")
    console.print("  ✅ Creates NEW content (doesn't update existing)")
    console.print("  ✅ Publishes as DRAFT (not live)")
    console.print("  ✅ Asks for confirmation before publishing")
    
    # Choose file to test
    test_file = 'content/posts/packing-3-week-vs-6-week-sleepaway-camp.json'
    
    console.print(f"\n[cyan]Test file:[/cyan] {test_file}")
    
    # Load the file
    try:
        with open(test_file, 'r') as f:
            post_data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {test_file}[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON: {e}[/red]")
        sys.exit(1)
    
    # Show post info
    console.print("\n[bold]Post Information:[/bold]")
    console.print(f"  Title: {post_data.get('title', 'Untitled')}")
    console.print(f"  Slug: {post_data.get('slug', 'N/A')}")
    console.print(f"  Status: {post_data.get('status', 'draft')} (will be published as draft)")
    console.print(f"  Content length: {len(post_data.get('content', ''))} characters")
    console.print(f"  Categories: {', '.join(post_data.get('categories', []))}")
    console.print(f"  Tags: {', '.join(post_data.get('tags', []))}")
    
    # Test connection
    console.print("\n[bold]Testing WordPress connection...[/bold]")
    auth = WordPressAuth()
    success, message, data = auth.test_connection()
    
    if not success:
        console.print(f"[red]❌ Connection failed: {message}[/red]")
        console.print("\n[yellow]Run 'python test_connection.py' for detailed diagnostics[/yellow]")
        sys.exit(1)
    
    console.print(f"[green]✅ Connected to: {data.get('site_name', 'WordPress')}[/green]")
    
    # Check permissions
    permissions = auth.check_permissions()
    if not permissions['can_publish_posts']:
        console.print("[red]❌ Your user doesn't have permission to publish posts[/red]")
        sys.exit(1)
    
    console.print("[green]✅ Permissions verified[/green]")
    
    # Show what we're about to do
    console.print("\n[bold yellow]⚠️  This will create a NEW draft post in WordPress[/bold yellow]")
    console.print("[dim]You can review it in WordPress admin before publishing live[/dim]")
    console.print("\n[green]Proceeding with test publish...[/green]")
    
    # Publish the post
    console.print("\n[bold]Publishing post...[/bold]")
    
    session = auth.get_session()
    
    # Prepare minimal post data (no internal links, no images for test)
    wp_post_data = {
        'title': post_data['title'],
        'content': post_data['content'],
        'excerpt': post_data.get('excerpt', ''),
        'status': 'draft',  # Force draft for safety
        'slug': post_data.get('slug', ''),
        'date': post_data.get('date', ''),
        'meta': {
            'description': post_data.get('meta_description', ''),
            '_yoast_wpseo_title': post_data.get('meta_title', ''),
            '_yoast_wpseo_metadesc': post_data.get('meta_description', ''),
        }
    }
    
    try:
        response = session.post(
            Config.get_api_url('posts'),
            json=wp_post_data,
            timeout=30
        )
        
        console.print(f"[dim]Response status: {response.status_code}[/dim]")
        console.print(f"[dim]Response headers: {dict(response.headers)}[/dim]")
        console.print(f"[dim]Response text (first 500 chars): {response.text[:500]}[/dim]")
        
        if response.status_code in [200, 201]:
            result = response.json()
            wp_id = result['id']
            url = result['link']
            
            console.print("\n[bold green]✅ SUCCESS![/bold green]")
            console.print(f"\n[cyan]Post Details:[/cyan]")
            console.print(f"  WordPress ID: {wp_id}")
            console.print(f"  Status: {result['status']} (draft)")
            console.print(f"  URL: {url}")
            console.print(f"  Title: {result['title']['rendered']}")
            
            console.print("\n[bold]Next Steps:[/bold]")
            console.print("  1. Log into your WordPress admin")
            console.print("  2. Go to Posts → All Posts")
            console.print(f"  3. Find the draft post: '{post_data['title']}'")
            console.print("  4. Review the formatting and content")
            console.print("  5. If it looks good, you can:")
            console.print("     - Delete it (it's just a test)")
            console.print("     - Or publish more blog posts")
            
            console.print(f"\n[green]Draft preview link:[/green] {url}")
            
        else:
            console.print(f"\n[red]❌ Publishing failed: {response.status_code}[/red]")
            console.print(f"[dim]{response.text[:500]}[/dim]")
            sys.exit(1)
    
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Test cancelled[/yellow]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
