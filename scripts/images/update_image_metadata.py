#!/usr/bin/env python3
"""
Image Metadata Updater for Camp Lakota
Updates WordPress images with generated metadata from CSV or JSON
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import print as rprint

from modules.auth import WordPressAuth
from config import Config

console = Console()

class ImageMetadataUpdater:
    def __init__(self):
        self.auth = WordPressAuth()
        self.session = self.auth.get_session()
        self.results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
    def load_metadata_from_json(self, file_path: str) -> List[Dict]:
        """Load metadata from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_metadata_from_csv(self, file_path: str) -> List[Dict]:
        """Load metadata from CSV file"""
        metadata_list = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert keywords back to list
                if row.get('keywords'):
                    row['keywords'] = [k.strip() for k in row['keywords'].split(',')]
                else:
                    row['keywords'] = []
                
                metadata_list.append(row)
        
        return metadata_list
    
    def update_single_image(self, metadata: Dict, dry_run: bool = False) -> bool:
        """Update a single image in WordPress"""
        image_id = int(metadata['id'])
        
        # Prepare update data
        update_data = {
            'title': metadata.get('new_title', ''),
            'alt_text': metadata.get('alt_text', ''),
            'caption': metadata.get('caption', ''),
            'description': metadata.get('description', '')
        }
        
        # Skip if no new metadata provided
        if not any(update_data.values()):
            self.results['skipped'].append({
                'id': image_id,
                'reason': 'No metadata provided'
            })
            return False
        
        if dry_run:
            console.print(f"[dim]DRY RUN: Would update image {image_id}[/dim]")
            return True
        
        try:
            media_url = f"{Config.get_api_url('media')}/{image_id}"
            response = self.session.post(
                media_url,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.results['success'].append({
                    'id': image_id,
                    'title': metadata.get('new_title', '')
                })
                return True
            else:
                self.results['failed'].append({
                    'id': image_id,
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
                })
                return False
                
        except Exception as e:
            self.results['failed'].append({
                'id': image_id,
                'error': str(e)
            })
            return False
    
    def update_batch(self, metadata_list: List[Dict], dry_run: bool = False):
        """Update a batch of images"""
        console.print(f"\n[cyan]{'DRY RUN: ' if dry_run else ''}Updating {len(metadata_list)} images...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Updating...", total=len(metadata_list))
            
            for metadata in metadata_list:
                self.update_single_image(metadata, dry_run=dry_run)
                progress.update(task, advance=1)
        
        # Display results
        self.display_results()
    
    def display_results(self):
        """Display update results"""
        console.print("\n[bold]Update Results:[/bold]\n")
        
        # Success table
        if self.results['success']:
            table = Table(title="Successfully Updated", style="green")
            table.add_column("Image ID", style="cyan")
            table.add_column("New Title", style="white")
            
            for item in self.results['success']:
                table.add_row(str(item['id']), item['title'][:60])
            
            console.print(table)
        
        # Failed table
        if self.results['failed']:
            table = Table(title="Failed Updates", style="red")
            table.add_column("Image ID", style="cyan")
            table.add_column("Error", style="red")
            
            for item in self.results['failed']:
                table.add_row(str(item['id']), item['error'][:60])
            
            console.print(table)
        
        # Skipped
        if self.results['skipped']:
            console.print(f"\n[yellow]Skipped {len(self.results['skipped'])} images (no metadata)[/yellow]")
        
        # Summary
        total = len(self.results['success']) + len(self.results['failed']) + len(self.results['skipped'])
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  [green]✓[/green] Success: {len(self.results['success'])}")
        console.print(f"  [red]✗[/red] Failed: {len(self.results['failed'])}")
        console.print(f"  [yellow]⊝[/yellow] Skipped: {len(self.results['skipped'])}")
        console.print(f"  [cyan]Total:[/cyan] {total}")


def main():
    console.print(Panel.fit(
        "[bold cyan]Camp Lakota Image Metadata Updater[/bold cyan]\n"
        "[dim]Step 3: Update WordPress with generated metadata[/dim]",
        border_style="cyan"
    ))
    
    # Look for metadata files (prefer work/ but keep root fallback)
    search_dirs = [Path("work") / "image-metadata", Path(".")]
    json_files = []
    csv_files = []
    for d in search_dirs:
        if not d.exists():
            continue
        json_files.extend(list(d.glob("image_metadata_generated*.json")))
        csv_files.extend(list(d.glob("image_metadata_generated*.csv")))
    
    if not json_files and not csv_files:
        console.print("\n[red]No metadata files found![/red]")
        console.print("[yellow]Looking for:[/yellow]")
        console.print("  • image_metadata_generated.json")
        console.print("  • image_metadata_generated.csv")
        console.print("\n[dim]Generate metadata first using the metadata generator[/dim]")
        return
    
    # Show available files
    console.print("\n[cyan]Found metadata files:[/cyan]")
    all_files = json_files + csv_files
    for i, f in enumerate(all_files, 1):
        console.print(f"  {i}. {f}")
    
    console.print("\n[yellow]This script will update WordPress images with the metadata from these files.[/yellow]")
    console.print("[yellow]Run with DRY_RUN=true to test without making changes.[/yellow]")
    
    # Check for dry run mode
    import os
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    if dry_run:
        console.print("\n[bold yellow]🔍 DRY RUN MODE - No changes will be made[/bold yellow]")
    else:
        console.print("\n[bold red]⚠️  LIVE MODE - Changes will be written to WordPress[/bold red]")
    
    # For now, just show what would happen
    console.print("\n[dim]To run the update:[/dim]")
    console.print("[dim]  python -m scripts.images.update_image_metadata[/dim]")
    console.print("\n[dim]To test first (recommended):[/dim]")
    console.print("[dim]  DRY_RUN=true python -m scripts.images.update_image_metadata[/dim]")


if __name__ == "__main__":
    main()
