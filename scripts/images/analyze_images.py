#!/usr/bin/env python3
"""
Image Metadata Analyzer for Camp Lakota
Downloads images from WordPress, prepares them for AI analysis, generates metadata
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from modules.auth import WordPressAuth
from config import Config

console = Console()

class ImageAnalyzer:
    def __init__(self):
        self.auth = WordPressAuth()
        self.session = self.auth.get_session()
        # Keep repo root clean: store downloads and batch JSON under work/
        self.work_dir = Path("work") / "image-metadata"
        self.images_dir = self.work_dir / "temp_images_for_analysis"
        self.batches_dir = self.work_dir / "batches"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.batches_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_all_media(self, missing_metadata_only=True):
        """Fetch all media items from WordPress"""
        console.print("\n[cyan]Fetching media library from WordPress...[/cyan]")
        
        all_media = []
        page = 1
        per_page = 100
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading images...", total=None)
            
            while True:
                response = self.session.get(
                    Config.get_api_url('media'),
                    params={
                        'per_page': per_page,
                        'page': page,
                        'media_type': 'image'
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                    
                media_batch = response.json()
                if not media_batch:
                    break
                    
                all_media.extend(media_batch)
                progress.update(task, description=f"Loaded {len(all_media)} images...")
                page += 1
        
        console.print(f"[green]✓[/green] Found {len(all_media)} total images")
        
        # Filter for images missing metadata
        if missing_metadata_only:
            needs_metadata = []
            for img in all_media:
                has_alt = bool(img.get('alt_text', '').strip())
                has_caption = bool(img.get('caption', {}).get('rendered', '').strip())
                title_is_generic = img['title']['rendered'].startswith('DSC') or \
                                 img['title']['rendered'].startswith('IMG') or \
                                 img['title']['rendered'].startswith('_')
                
                if not has_alt or not has_caption or title_is_generic:
                    needs_metadata.append(img)
            
            console.print(f"[yellow]⚠[/yellow] {len(needs_metadata)} images need metadata")
            return needs_metadata
        
        return all_media
    
    def download_image_batch(self, media_items: List[Dict], batch_size=20):
        """Download a batch of images for analysis"""
        console.print(f"\n[cyan]Downloading batch of {min(batch_size, len(media_items))} images...[/cyan]")
        
        downloaded = []
        actual_size = min(batch_size, len(media_items))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", total=actual_size)
            
            for i, item in enumerate(media_items[:actual_size]):
                image_url = item['source_url']
                image_id = item['id']
                
                # Get file extension - handle .avif and other formats
                url_path = Path(image_url)
                ext = url_path.suffix if url_path.suffix else '.jpg'
                local_path = self.images_dir / f"{image_id}{ext}"
                
                try:
                    img_response = requests.get(image_url, timeout=30, allow_redirects=True)
                    
                    if img_response.status_code == 200 and len(img_response.content) > 0:
                        with open(local_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded.append({
                            'id': image_id,
                            'url': image_url,
                            'local_path': str(local_path),
                            'current_title': item['title']['rendered'],
                            'current_alt': item.get('alt_text', ''),
                            'current_caption': item.get('caption', {}).get('rendered', ''),
                        })
                        console.print(f"[green]✓[/green] Downloaded {image_id}: {item['title']['rendered']}")
                    else:
                        console.print(f"[yellow]⚠[/yellow] Failed to download {image_id}: Status {img_response.status_code}")
                        
                except Exception as e:
                    console.print(f"[red]✗[/red] Error downloading {image_id}: {e}")
                
                progress.update(task, advance=1)
        
        console.print(f"\n[green]✓[/green] Downloaded {len(downloaded)} images successfully")
        return downloaded
    
    def save_analysis_batch(self, batch_data: List[Dict], batch_num: int):
        """Save batch data for manual analysis"""
        output_file = self.batches_dir / f"image_batch_{batch_num}_for_analysis.json"

        with open(output_file, 'w', encoding="utf-8") as f:
            json.dump(batch_data, f, indent=2)
        
        console.print(f"[green]✓[/green] Saved batch data to: {output_file}")
        return str(output_file)
    
    def display_summary(self, media_items: List[Dict]):
        """Display summary table of images needing metadata"""
        table = Table(title="Images Needing Metadata")
        table.add_column("ID", style="cyan")
        table.add_column("Current Title", style="yellow")
        table.add_column("Has Alt?", style="magenta")
        table.add_column("Has Caption?", style="magenta")
        
        for item in media_items[:20]:  # Show first 20
            has_alt = "✓" if item.get('alt_text', '').strip() else "✗"
            has_caption = "✓" if item.get('caption', {}).get('rendered', '').strip() else "✗"
            
            table.add_row(
                str(item['id']),
                item['title']['rendered'][:40],
                has_alt,
                has_caption
            )
        
        if len(media_items) > 20:
            table.add_row("...", f"...and {len(media_items) - 20} more", "", "")
        
        console.print(table)


def main():
    console.print(Panel.fit(
        "[bold cyan]Camp Lakota Image Metadata Analyzer[/bold cyan]\n"
        "[dim]Step 1: Identify and prepare images for metadata generation[/dim]",
        border_style="cyan"
    ))
    
    analyzer = ImageAnalyzer()
    
    # Step 1: Fetch all images needing metadata
    media_items = analyzer.fetch_all_media(missing_metadata_only=True)
    
    if not media_items:
        console.print("[green]✓[/green] All images have proper metadata!")
        return
    
    # Step 2: Display summary
    analyzer.display_summary(media_items)
    
    # Step 3: Ask about batch processing
    console.print(f"\n[bold yellow]Found {len(media_items)} images needing metadata[/bold yellow]")
    console.print("\n[cyan]Options:[/cyan]")
    console.print("1. Process in small batches (recommended - 20 at a time)")
    console.print("2. Export list to CSV for review")
    console.print("3. Show me the first 10 image URLs to review")
    
    console.print("\n[dim]Next step: We'll download a batch and I'll analyze each image[/dim]")
    console.print("[dim]to generate professional metadata (title, alt text, caption, description)[/dim]")
    
    # For now, just prepare the first batch
    console.print("\n[cyan]Preparing first batch of 10 images for analysis...[/cyan]")
    batch_data = analyzer.download_image_batch(media_items, batch_size=10)
    output_file = analyzer.save_analysis_batch(batch_data, batch_num=1)
    
    console.print("\n[bold green]✓ Batch Ready for Analysis![/bold green]")
    console.print(f"\nImages downloaded to: [cyan]{analyzer.images_dir}[/cyan]")
    console.print(f"Batch data saved to: [cyan]{output_file}[/cyan]")
    
    console.print("\n[yellow]Next Step:[/yellow]")
    console.print("Run the image metadata generator to analyze these images")
    console.print("and create professional metadata for each one.")


if __name__ == "__main__":
    main()
