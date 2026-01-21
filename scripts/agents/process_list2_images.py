#!/usr/bin/env python3
"""
Agent 2: Process List 2 Images for Camp Lakota
Processes all 48 images: views each, generates metadata, updates WordPress
"""

import json
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from modules.auth import WordPressAuth
from config import Config

console = Console()

WORK_AGENTS_DIR = Path("work") / "agents"
WORK_IMAGE_INPUTS_DIR = Path("work") / "image-metadata" / "inputs"


def _pick_existing_path(*candidates: Path) -> Path:
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


class List2Processor:
    """Process List 2 images"""
    
    def __init__(self):
        self.auth = WordPressAuth()
        self.session = self.auth.get_session()
        self.processed_ids = set()
        self.questions = []
        self.results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        # Load tracking
        self.tracking_file = _pick_existing_path(
            WORK_AGENTS_DIR / "agent2_done_ids.txt",
            Path("agent2_done_ids.txt"),  # legacy root location
        )
        self.questions_file = _pick_existing_path(
            WORK_AGENTS_DIR / "agent2_questions.txt",
            Path("agent2_questions.txt"),  # legacy root location
        )
        self._load_tracking()
    
    def _load_tracking(self):
        """Load already processed IDs"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.isdigit():
                        self.processed_ids.add(int(line))
            if self.processed_ids:
                console.print(f"[dim]Loaded {len(self.processed_ids)} already processed IDs[/dim]")
    
    def _save_tracking(self, image_id: int):
        """Save processed ID"""
        WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'a') as f:
            f.write(f"{image_id}\n")
        self.processed_ids.add(image_id)
    
    def _save_question(self, image_id: int, url: str, question: str):
        """Save question"""
        entry = f"ID: {image_id}\nURL: {url}\nQuestion: {question}\n\n"
        WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.questions_file, 'a') as f:
            f.write(entry)
    
    def load_images(self) -> List[Dict]:
        """Load image list"""
        json_path = _pick_existing_path(
            WORK_IMAGE_INPUTS_DIR / "image_remaining_unprocessed_part2.json",
            Path("image_remaining_unprocessed_part2.json"),  # legacy root location
        )
        if not json_path.exists():
            raise FileNotFoundError("Could not find image_remaining_unprocessed_part2.json (expected in work/image-metadata/inputs/ or repo root)")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_metadata(self, image_id: int, metadata: Dict) -> bool:
        """Update WordPress image metadata"""
        try:
            update_data = {
                'title': metadata.get('title', ''),
                'alt_text': metadata.get('alt_text', ''),
                'caption': metadata.get('caption', ''),
                'description': metadata.get('description', '')
            }
            
            # Remove empty fields
            update_data = {k: v for k, v in update_data.items() if v}
            
            if not update_data:
                return False
            
            media_url = f"{Config.get_api_url('media')}/{image_id}"
            response = self.session.post(media_url, json=update_data, timeout=30)
            
            if response.status_code == 200:
                self.results['success'].append({
                    'id': image_id,
                    'title': metadata.get('title', '')[:50]
                })
                return True
            else:
                error_msg = f"HTTP {response.status_code}"
                if response.text:
                    error_msg += f": {response.text[:100]}"
                self.results['failed'].append({
                    'id': image_id,
                    'error': error_msg
                })
                return False
                
        except Exception as e:
            self.results['failed'].append({
                'id': image_id,
                'error': str(e)[:100]
            })
            return False
    
    def display_results(self):
        """Display results"""
        console.print("\n[bold]Processing Results:[/bold]\n")
        
        if self.results['success']:
            table = Table(title="Successfully Updated", style="green")
            table.add_column("Image ID", style="cyan")
            table.add_column("Title", style="white")
            
            for item in self.results['success'][:20]:  # Show first 20
                table.add_row(str(item['id']), item['title'])
            
            if len(self.results['success']) > 20:
                console.print(f"[dim]... and {len(self.results['success']) - 20} more[/dim]")
            
            console.print(table)
        
        if self.results['failed']:
            table = Table(title="Failed Updates", style="red")
            table.add_column("Image ID", style="cyan")
            table.add_column("Error", style="red")
            
            for item in self.results['failed']:
                table.add_row(str(item['id']), item['error'][:60])
            
            console.print(table)
        
        # Summary
        total = len(self.results['success']) + len(self.results['failed'])
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  [green]✓[/green] Success: {len(self.results['success'])}")
        console.print(f"  [red]✗[/red] Failed: {len(self.results['failed'])}")
        console.print(f"  [cyan]Total:[/cyan] {total}")


# Metadata dictionary - populated as we process images
METADATA = {}


def main():
    """Main processing function"""
    console.print(Panel.fit(
        "[bold cyan]Agent 2: Camp Lakota List 2 Image Processor[/bold cyan]\n"
        "[dim]Processing 48 images (IDs 2134-1849)[/dim]",
        border_style="cyan"
    ))
    
    processor = List2Processor()
    
    try:
        images = processor.load_images()
        console.print(f"\n[green]✓[/green] Loaded {len(images)} images")
        
        # Filter out already processed
        remaining = [img for img in images if img['id'] not in processor.processed_ids]
        
        if not remaining:
            console.print("\n[yellow]All images have already been processed![/yellow]")
            return
        
        if len(remaining) < len(images):
            console.print(f"[dim]Skipping {len(images) - len(remaining)} already processed[/dim]")
        
        console.print(f"\n[cyan]Processing {len(remaining)} remaining images...[/cyan]\n")
        
        # Process each image
        # Metadata will be added to METADATA dict as we view and process images
        for image in remaining:
            image_id = image['id']
            
            if image_id in METADATA:
                metadata = METADATA[image_id]
                if processor.update_metadata(image_id, metadata):
                    processor._save_tracking(image_id)
                    console.print(f"[green]✓[/green] Updated ID {image_id}")
                else:
                    console.print(f"[red]✗[/red] Failed ID {image_id}")
            else:
                console.print(f"[yellow]⊝[/yellow] No metadata for ID {image_id} yet - will be processed")
        
        processor.display_results()
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
