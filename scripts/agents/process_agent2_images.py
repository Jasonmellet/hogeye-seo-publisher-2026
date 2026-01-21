#!/usr/bin/env python3
"""
Agent 2: Process List 2 WordPress Images
Processes 48 images, views each in browser, generates metadata, and updates WordPress
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

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


class Agent2Processor:
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
        
        # Tracking files
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
    
    def _save_tracking(self, image_id: int):
        """Save processed ID"""
        WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'a') as f:
            f.write(f"{image_id}\n")
        self.processed_ids.add(image_id)
    
    def _save_question(self, image_id: int, url: str, question: str):
        """Save question about an image"""
        entry = f"ID: {image_id}\nURL: {url}\nQuestion: {question}\n\n"
        WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.questions_file, 'a') as f:
            f.write(entry)
    
    def load_image_list(self) -> List[Dict]:
        """Load image list from JSON"""
        json_path = _pick_existing_path(
            WORK_IMAGE_INPUTS_DIR / "image_remaining_unprocessed_part2.json",
            Path("image_remaining_unprocessed_part2.json"),  # legacy root location
        )
        if not json_path.exists():
            raise FileNotFoundError("Could not find image_remaining_unprocessed_part2.json")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_image_metadata(self, image_id: int, metadata: Dict) -> bool:
        """Update WordPress image metadata via API"""
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
            response = self.session.post(
                media_url,
                json=update_data,
                timeout=30
            )
            
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
        """Display processing results"""
        console.print("\n[bold]Processing Results:[/bold]\n")
        
        if self.results['success']:
            table = Table(title="Successfully Updated", style="green")
            table.add_column("Image ID", style="cyan")
            table.add_column("Title", style="white")
            
            for item in self.results['success']:
                table.add_row(str(item['id']), item['title'])
            
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


def generate_metadata_for_image(image_data: Dict, image_description: str = None) -> Dict:
    """
    Generate metadata for an image based on its data and description
    This will be called after viewing each image
    """
    image_id = image_data['id']
    title = image_data.get('title', '')
    source_url = image_data.get('source_url', '')
    
    # This function will be populated with actual metadata generation logic
    # For now, return empty dict - will be filled per image
    return {
        'title': '',
        'alt_text': '',
        'caption': '',
        'description': ''
    }


def main():
    """Main processing function"""
    console.print(Panel.fit(
        "[bold cyan]Agent 2: Camp Lakota Image Metadata Processor[/bold cyan]\n"
        "[dim]Processing List 2: 48 images (IDs 2134-1849)[/dim]",
        border_style="cyan"
    ))
    
    processor = Agent2Processor()
    
    try:
        images = processor.load_image_list()
        console.print(f"\n[green]✓[/green] Loaded {len(images)} images")
        
        # Filter out already processed
        remaining = [img for img in images if img['id'] not in processor.processed_ids]
        
        if not remaining:
            console.print("\n[yellow]All images have already been processed![/yellow]")
            return
        
        console.print(f"\n[cyan]Processing {len(remaining)} remaining images...[/cyan]\n")
        
        # Process each image
        for i, image in enumerate(remaining, 1):
            image_id = image['id']
            source_url = image['source_url']
            
            console.print(f"\n[{i}/{len(remaining)}] Processing ID {image_id}")
            console.print(f"[dim]URL: {source_url}[/dim]")
            
            # Metadata will be generated by viewing the image
            # For now, we'll process them one by one with manual review
            
        processor.display_results()
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
