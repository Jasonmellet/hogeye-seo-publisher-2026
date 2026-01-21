#!/usr/bin/env python3
"""
Camp Lakota WordPress Content Publisher
Main script to publish pages and posts to WordPress
"""

import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import Config
from modules.auth import WordPressAuth
from modules.content import ContentProcessor
from modules.images import ImageUploader
from modules.metadata import MetadataHandler
from modules.links import InternalLinkManager

console = Console()


def print_header():
    """Print welcome header"""
    console.print(Panel.fit(
        "[bold cyan]Camp Lakota WordPress Publisher[/bold cyan]\n"
        "[dim]Publishing landing pages and blog posts to WordPress[/dim]",
        border_style="cyan"
    ))


def test_authentication():
    """Test WordPress authentication"""
    console.print("\n[bold]1. Testing WordPress Connection...[/bold]")
    
    auth = WordPressAuth()
    success, message, data = auth.test_connection()
    
    if not success:
        console.print(f"[red]❌ Authentication Failed:[/red] {message}")
        return None, None
    
    console.print(f"[green]✅ {message}[/green]")
    
    if data:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[cyan]Site:[/cyan]", data.get('site_name', 'Unknown'))
        table.add_row("[cyan]User:[/cyan]", data.get('user_name', 'Unknown'))
        table.add_row("[cyan]User ID:[/cyan]", str(data.get('user_id', 'Unknown')))
        console.print(table)
    
    # Check permissions
    console.print("\n[dim]Checking permissions...[/dim]")
    permissions = auth.check_permissions()
    
    if not permissions['can_publish_posts'] or not permissions['can_publish_pages']:
        console.print("[yellow]⚠️  Warning: Limited permissions detected[/yellow]")
        if not permissions['can_publish_posts']:
            console.print("   - Cannot publish posts")
        if not permissions['can_publish_pages']:
            console.print("   - Cannot publish pages")
        
        if input("\nContinue anyway? (y/n): ").lower() != 'y':
            return None, None
    
    return auth, auth.get_session()


def load_content():
    """Load all content files"""
    console.print("\n[bold]2. Loading Content Files...[/bold]")
    
    processor = ContentProcessor()
    
    pages = processor.load_pages()
    posts = processor.load_posts()
    
    if not pages and not posts:
        console.print("[red]❌ No content files found![/red]")
        console.print(f"   - Pages directory: {Config.PAGES_DIR}")
        console.print(f"   - Posts directory: {Config.POSTS_DIR}")
        return None, None, None
    
    console.print(f"\n[green]✅ Loaded {len(pages)} page(s) and {len(posts)} post(s)[/green]")
    
    # Validate content
    console.print("\n[dim]Validating content...[/dim]")
    all_valid = True
    
    for page in pages:
        valid, errors = processor.validate_page(page)
        if not valid:
            console.print(f"[red]❌ Invalid page: {page.get('title', 'Unknown')}[/red]")
            for error in errors:
                console.print(f"   - {error}")
            all_valid = False
    
    for post in posts:
        valid, errors = processor.validate_post(post)
        if not valid:
            console.print(f"[red]❌ Invalid post: {post.get('title', 'Unknown')}[/red]")
            for error in errors:
                console.print(f"   - {error}")
            all_valid = False
    
    if not all_valid:
        console.print("\n[red]❌ Content validation failed. Please fix errors and try again.[/red]")
        return None, None, None
    
    console.print("[green]✅ All content validated successfully[/green]")
    
    return processor, pages, posts


def publish_pages(session, processor, pages, image_uploader, link_manager):
    """Publish landing pages"""
    if not pages:
        return []
    
    console.print("\n[bold]3. Publishing Landing Pages...[/bold]")
    
    published_pages = []
    
    for idx, page in enumerate(pages, 1):
        title = page.get('title', 'Untitled')
        console.print(f"\n[cyan]📄 Publishing page {idx}/{len(pages)}: {title}[/cyan]")
        
        if Config.is_dry_run():
            console.print("[yellow]   [DRY RUN] Would publish page[/yellow]")
            continue
        
        # Upload featured image if specified
        if page.get('featured_image'):
            media_id = image_uploader.upload_image(
                page['featured_image'],
                metadata={
                    'alt_text': page.get('featured_image_alt', title),
                    'title': title
                }
            )
            if media_id:
                page['featured_media'] = media_id
        
        # Prepare page data
        page_data = processor.prepare_page_data(page)
        
        # Publish page
        try:
            response = session.post(
                Config.get_api_url('pages'),
                json=page_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                wp_id = result['id']
                url = result['link']
                slug = result['slug']
                
                console.print(f"[green]   ✅ Published: {url}[/green]")
                
                # Register for internal linking
                link_manager.register_published_content(slug, url, wp_id)
                
                published_pages.append({
                    'id': wp_id,
                    'slug': slug,
                    'url': url,
                    'title': title,
                    'content': page_data['content']
                })
            else:
                console.print(f"[red]   ❌ Failed: {response.status_code}[/red]")
                console.print(f"[dim]   {response.text[:200]}[/dim]")
        
        except Exception as e:
            console.print(f"[red]   ❌ Error: {e}[/red]")
    
    return published_pages


def publish_posts(session, processor, posts, image_uploader, link_manager):
    """Publish blog posts"""
    if not posts:
        return []
    
    console.print("\n[bold]4. Publishing Blog Posts...[/bold]")
    
    published_posts = []
    
    for idx, post in enumerate(posts, 1):
        title = post.get('title', 'Untitled')
        console.print(f"\n[cyan]📰 Publishing post {idx}/{len(posts)}: {title}[/cyan]")
        
        if Config.is_dry_run():
            console.print("[yellow]   [DRY RUN] Would publish post[/yellow]")
            continue
        
        # Upload featured image if specified
        if post.get('featured_image'):
            media_id = image_uploader.upload_image(
                post['featured_image'],
                metadata={
                    'alt_text': post.get('featured_image_alt', title),
                    'title': title
                }
            )
            if media_id:
                post['featured_media'] = media_id
        
        # Prepare post data
        post_data = processor.prepare_post_data(post)
        
        # Publish post
        try:
            response = session.post(
                Config.get_api_url('posts'),
                json=post_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                wp_id = result['id']
                url = result['link']
                slug = result['slug']
                
                console.print(f"[green]   ✅ Published: {url}[/green]")
                
                # Register for internal linking
                link_manager.register_published_content(slug, url, wp_id)
                
                published_posts.append({
                    'id': wp_id,
                    'slug': slug,
                    'url': url,
                    'title': title,
                    'content': post_data['content']
                })
            else:
                console.print(f"[red]   ❌ Failed: {response.status_code}[/red]")
                console.print(f"[dim]   {response.text[:200]}[/dim]")
        
        except Exception as e:
            console.print(f"[red]   ❌ Error: {e}[/red]")
    
    return published_posts


def process_internal_links(link_manager, published_pages, published_posts):
    """Process internal links in published content"""
    console.print("\n[bold]5. Processing Internal Links...[/bold]")
    
    if Config.is_dry_run():
        console.print("[yellow][DRY RUN] Would process internal links[/yellow]")
        return
    
    # Process pages
    if published_pages:
        link_manager.process_content_links(published_pages, 'pages')
    
    # Process posts
    if published_posts:
        link_manager.process_content_links(published_posts, 'posts')
    
    console.print("[green]✅ Internal linking complete[/green]")


def print_summary(published_pages, published_posts):
    """Print publication summary"""
    console.print("\n" + "="*60)
    console.print("\n[bold green]🎉 Publication Complete![/bold green]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Landing Pages", str(len(published_pages)))
    table.add_row("Blog Posts", str(len(published_posts)))
    table.add_row("Total", str(len(published_pages) + len(published_posts)))
    
    console.print(table)
    
    if published_pages:
        console.print("\n[bold]Published Pages:[/bold]")
        for page in published_pages:
            console.print(f"  ✅ {page['title']}")
            console.print(f"     [dim]{page['url']}[/dim]")
    
    if published_posts:
        console.print("\n[bold]Published Posts:[/bold]")
        for post in published_posts:
            console.print(f"  ✅ {post['title']}")
            console.print(f"     [dim]{post['url']}[/dim]")
    
    console.print("\n" + "="*60 + "\n")


def main():
    """Main execution function"""
    try:
        # Print header
        print_header()
        
        # Check configuration
        try:
            Config.validate()
            Config.ensure_directories()
        except ValueError as e:
            console.print(f"\n[red]{e}[/red]\n")
            sys.exit(1)
        
        # Show dry run status
        if Config.is_dry_run():
            console.print("\n[yellow]⚠️  DRY RUN MODE - No actual publishing will occur[/yellow]")
        
        # Test authentication
        auth, session = test_authentication()
        if not auth or not session:
            sys.exit(1)
        
        # Load content
        processor, pages, posts = load_content()
        if not processor:
            sys.exit(1)
        
        # Initialize modules
        image_uploader = ImageUploader(session)
        link_manager = InternalLinkManager(session)
        
        # Publish content
        published_pages = publish_pages(session, processor, pages, image_uploader, link_manager)
        published_posts = publish_posts(session, processor, posts, image_uploader, link_manager)
        
        # Process internal links
        if published_pages or published_posts:
            process_internal_links(link_manager, published_pages, published_posts)
        
        # Print summary
        if not Config.is_dry_run():
            print_summary(published_pages, published_posts)
        else:
            console.print("\n[yellow]DRY RUN COMPLETE - Set DRY_RUN=false in .env to publish for real[/yellow]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Publishing cancelled by user[/yellow]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
