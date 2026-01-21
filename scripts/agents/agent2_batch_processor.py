#!/usr/bin/env python3
"""
Agent 2: Batch Process List 2 Images
Views images, generates metadata, and updates WordPress
"""

import json
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
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


def load_images() -> List[Dict]:
    """Load image list"""
    json_path = _pick_existing_path(
        WORK_IMAGE_INPUTS_DIR / "image_remaining_unprocessed_part2.json",
        Path("image_remaining_unprocessed_part2.json"),  # legacy root location
    )
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_image_metadata(session, image_id: int, metadata: Dict) -> bool:
    """Update WordPress image metadata"""
    try:
        update_data = {
            'title': metadata.get('title', ''),
            'alt_text': metadata.get('alt_text', ''),
            'caption': metadata.get('caption', ''),
            'description': metadata.get('description', '')
        }
        
        update_data = {k: v for k, v in update_data.items() if v}
        
        if not update_data:
            return False
        
        media_url = f"{Config.get_api_url('media')}/{image_id}"
        response = session.post(media_url, json=update_data, timeout=30)
        
        return response.status_code == 200
    except Exception as e:
        console.print(f"[red]Error updating {image_id}: {e}[/red]")
        return False


def save_tracking(image_id: int):
    """Save processed ID"""
    WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    tracking_file = _pick_existing_path(
        WORK_AGENTS_DIR / "agent2_done_ids.txt",
        Path("agent2_done_ids.txt"),  # legacy root location
    )
    with open(tracking_file, 'a', encoding="utf-8") as f:
        f.write(f"{image_id}\n")


# Metadata for images - will be populated as we view them
IMAGE_METADATA = {}


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]Agent 2: Batch Image Processor[/bold cyan]",
        border_style="cyan"
    ))
    
    images = load_images()
    console.print(f"\n[green]✓[/green] Loaded {len(images)} images")
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Process images
    success_count = 0
    failed_count = 0
    
    for image in images:
        image_id = image['id']
        console.print(f"\n[cyan]Processing ID {image_id}...[/cyan]")
        
        # Metadata will be added to IMAGE_METADATA dict as we process
        if image_id in IMAGE_METADATA:
            metadata = IMAGE_METADATA[image_id]
            if update_image_metadata(session, image_id, metadata):
                save_tracking(image_id)
                success_count += 1
                console.print(f"[green]✓[/green] Updated ID {image_id}")
            else:
                failed_count += 1
                console.print(f"[red]✗[/red] Failed ID {image_id}")
        else:
            console.print(f"[yellow]⊝[/yellow] No metadata for ID {image_id} yet")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]Success:[/green] {success_count}")
    console.print(f"  [red]Failed:[/red] {failed_count}")
