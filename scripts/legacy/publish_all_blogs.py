#!/usr/bin/env python3
"""
Bulk Blog Post Publisher (Canonical)

DEPRECATED BEHAVIOR NOTICE:
- This script used to publish raw content directly.
- It now delegates to the canonical pipeline in `modules/publish_pipeline.py`
  so monthly publishing is consistent and validated.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config
from modules.auth import WordPressAuth
from modules.publish_pipeline import PublishOptions, PublishPipeline

console = Console()

def load_blog_posts():
    """Load all blog post JSON files"""
    posts_dir = Path('content/posts')
    
    if not posts_dir.exists():
        console.print(f"[red]Posts directory not found: {posts_dir}[/red]")
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
        "[bold cyan]Bulk Blog Post Publisher[/bold cyan]\n"
        "[dim]Publishing all blog posts as drafts[/dim]",
        border_style="cyan"
    ))
    
    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"\n[red]Configuration Error:[/red]\n{e}\n")
        sys.exit(1)
    
    # Show safety features
    console.print("\n[bold]Safety Features:[/bold]")
    console.print("  ✅ Checks for existing posts to avoid duplicates")
    console.print("  ✅ All posts published as DRAFT (not live)")
    console.print("  ✅ Handles WordPress PHP warnings gracefully")
    console.print("  ✅ Shows detailed progress for each post")
    
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
        console.print("[red]❌ No blog posts found to publish[/red]")
        sys.exit(1)
    
    console.print(f"[green]✅ Found {len(posts)} blog post(s)[/green]")
    
    # Show posts to be published
    console.print("\n[bold]Posts to publish:[/bold]")
    for idx, post in enumerate(posts, 1):
        console.print(f"  {idx}. {post['title']}")
        console.print(f"     [dim]Slug: {post.get('slug', 'N/A')}[/dim]")
    
    console.print("\n[green]Starting publication (canonical pipeline)...[/green]\n")
    
    # Get session
    session = auth.get_session()
    pipeline = PublishPipeline(session)
    options = PublishOptions(status="draft")
    
    # Track results
    results = {
        'created': [],
        'skipped': [],
        'failed': []
    }
    
    # Publish each post
    for idx, post_data in enumerate(posts, 1):
        title = post_data['title']
        slug = post_data.get('slug', '') or ''
        source_file = post_data.get('_source_file', '')
        
        console.print(f"\n[cyan]━━━ Post {idx}/{len(posts)} ━━━[/cyan]")
        console.print(f"[bold]{title}[/bold]")

        # Determine absolute source path
        source_path = str(Path("content/posts") / source_file) if source_file else None
        if not source_path:
            results["failed"].append({"title": title, "error": "Missing _source_file"})
            continue

        console.print("  [dim]Publishing via canonical pipeline...[/dim]")
        wp_id, validation = pipeline.publish_from_file(source_path, content_type="posts", options=options)

        if wp_id is None:
            console.print("  [red]❌ Failed to publish[/red]")
            for e in validation.errors:
                console.print(f"  [red]- {e}[/red]")
            results["failed"].append({"title": title, "error": "; ".join(validation.errors) or "Unknown error"})
            continue

        if not validation.ok:
            console.print("  [yellow]⚠️  Published but failed validation (left as draft)[/yellow]")
            for e in validation.errors:
                console.print(f"  [red]- {e}[/red]")
            for w in validation.warnings:
                console.print(f"  [yellow]- {w}[/yellow]")
            results["failed"].append({"title": title, "error": "; ".join(validation.errors) or "Validation failed"})
            continue

        console.print(f"  [green]✅ Published successfully![/green]")
        for w in validation.warnings:
            console.print(f"  [yellow]- {w}[/yellow]")
        results["created"].append({"title": title, "id": wp_id, "status": "draft"})
    
    # Print summary
    console.print("\n" + "━" * 60)
    console.print("\n[bold green]📊 Publication Summary[/bold green]\n")
    
    summary_table = Table(show_header=True, header_style="bold cyan")
    summary_table.add_column("Result", style="cyan")
    summary_table.add_column("Count", justify="right", style="green")
    
    summary_table.add_row("✅ Created", str(len(results['created'])))
    summary_table.add_row("⚠️  Skipped (already exist)", str(len(results['skipped'])))
    summary_table.add_row("❌ Failed", str(len(results['failed'])))
    summary_table.add_row("━" * 20, "━" * 5)
    summary_table.add_row("Total Processed", str(len(posts)))
    
    console.print(summary_table)
    
    # Show created posts
    if results['created']:
        console.print("\n[bold green]✅ Successfully Created:[/bold green]")
        for post in results['created']:
            console.print(f"  • {post['title']}")
            console.print(f"    [dim]ID: {post['id']} | Status: {post['status']}[/dim]")
            if post['url']:
                console.print(f"    [dim]{post['url']}[/dim]")
    
    # Show skipped posts
    if results['skipped']:
        console.print("\n[bold yellow]⚠️  Skipped (Already Exist):[/bold yellow]")
        for post in results['skipped']:
            console.print(f"  • {post['title']}")
            console.print(f"    [dim]ID: {post['id']} | Status: {post['status']}[/dim]")
    
    # Show failed posts
    if results['failed']:
        console.print("\n[bold red]❌ Failed:[/bold red]")
        for post in results['failed']:
            console.print(f"  • {post['title']}")
            console.print(f"    [dim]{post['error'][:100]}...[/dim]")
    
    # Next steps
    console.print("\n[bold]📝 Next Steps:[/bold]")
    console.print("  1. Log into WordPress admin")
    console.print("  2. Go to Posts → All Posts")
    console.print("  3. Review all draft posts")
    console.print("  4. Fix any posts that failed validation, then re-run for those files")
    console.print("  5. After everything is clean, publish posts live")
    
    console.print("\n" + "━" * 60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Publishing cancelled[/yellow]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
