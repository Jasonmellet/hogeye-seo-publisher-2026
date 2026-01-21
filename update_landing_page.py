#!/usr/bin/env python3
"""
Update Landing Page - Simple Workflow:
1. Find existing page
2. Remove old content
3. Add new formatted content
4. Set to draft (for preview)
5. When approved, publish it
"""

from modules.auth import WordPressAuth
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modules.publish_pipeline import PublishOptions, PublishPipeline

console = Console()


def update_landing_page(json_file: str):
    """Update existing landing page with new content (canonical pipeline)"""
    
    console.print(Panel.fit("[bold cyan]Update Landing Page[/bold cyan]"))

    console.print(f"\n[cyan]Publishing page via canonical pipeline from {json_file}...[/cyan]")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()

    pipeline = PublishPipeline(session)
    wp_id, validation = pipeline.publish_from_file(
        json_file,
        content_type="pages",
        options=PublishOptions(status="draft", use_acf_blocks=True),
    )

    if wp_id is None:
        console.print("\n[bold red]❌ Update failed[/bold red]")
        for e in validation.errors:
            console.print(f"[red]- {e}[/red]")
        for w in validation.warnings:
            console.print(f"[yellow]- {w}[/yellow]")
        return

    console.print(f"\n[bold green]✅ Update Complete![/bold green]\n")

    table = Table(title="Page Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Page ID", str(wp_id))
    table.add_row("Status", "draft")
    table.add_row("Slug", "(see WP admin)")

    console.print(table)

    if not validation.ok:
        console.print("\n[bold yellow]⚠ Validation issues (kept as draft):[/bold yellow]")
        for e in validation.errors:
            console.print(f"[red]- {e}[/red]")
        for w in validation.warnings:
            console.print(f"[yellow]- {w}[/yellow]")

    console.print(f"\n[bold]Next Steps:[/bold]")
    console.print(f"  1. [yellow]Preview the page[/yellow] in WordPress admin (it's in draft status)")
    console.print(f"  2. [yellow]When approved[/yellow], run: python3 publish_draft_page.py {wp_id}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'content/pages/water-sports-update.json'
    
    update_landing_page(json_file)
