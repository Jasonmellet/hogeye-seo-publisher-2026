#!/usr/bin/env python3
"""
Agent 2: Complete List 2 Image Processor
Processes all 48 images systematically
"""

import json
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

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


# Complete metadata for all 48 images
# This will be populated as we view and process each image
ALL_METADATA = {
    # Image 2134 - Camp Lakota Logo (cropped)
    2134: {
        "title": "Camp Lakota Logo",
        "alt_text": "Camp Lakota circular logo with CL monogram, established 1924, on Masten Lake",
        "caption": "The official Camp Lakota logo featuring the camp monogram and founding year.",
        "description": "Camp Lakota official logo displays the camp circular emblem with the intertwined CL monogram at its center. The logo includes the text CAMP LAKOTA and ON MASTEN LAKE - EST. 1924, representing the camp location and over 100 years of history as a residential summer camp in Wurtsboro, New York."
    },
    # Additional metadata will be added as we process each image
}


def update_image(session, image_id: int, metadata: Dict) -> bool:
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


def main():
    """Process all images"""
    console.print(Panel.fit(
        "[bold cyan]Agent 2: Complete List 2 Processor[/bold cyan]",
        border_style="cyan"
    ))
    
    # Load images
    json_path = _pick_existing_path(
        WORK_IMAGE_INPUTS_DIR / "image_remaining_unprocessed_part2.json",
        Path("image_remaining_unprocessed_part2.json"),  # legacy root location
    )
    with open(json_path, 'r') as f:
        images = json.load(f)
    
    console.print(f"\n[green]✓[/green] Loaded {len(images)} images")
    
    # Load tracking
    processed = set()
    tracking_file = _pick_existing_path(
        WORK_AGENTS_DIR / "agent2_done_ids.txt",
        Path("agent2_done_ids.txt"),  # legacy root location
    )
    if tracking_file.exists():
        with open(tracking_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and line.isdigit():
                    processed.add(int(line))
        if processed:
            console.print(f"[dim]Skipping {len(processed)} already processed[/dim]")
    
    # Authenticate
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Process images
    success = 0
    failed = 0
    skipped = 0
    
    for image in images:
        image_id = image['id']
        
        if image_id in processed:
            skipped += 1
            continue
        
        if image_id not in ALL_METADATA:
            console.print(f"[yellow]⊝[/yellow] No metadata for ID {image_id} yet")
            continue
        
        metadata = ALL_METADATA[image_id]
        if update_image(session, image_id, metadata):
            save_tracking(image_id)
            success += 1
            console.print(f"[green]✓[/green] Updated ID {image_id}: {metadata['title'][:40]}")
        else:
            failed += 1
            console.print(f"[red]✗[/red] Failed ID {image_id}")
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]Success:[/green] {success}")
    console.print(f"  [red]Failed:[/red] {failed}")
    console.print(f"  [yellow]Skipped:[/yellow] {skipped}")


if __name__ == "__main__":
    main()
