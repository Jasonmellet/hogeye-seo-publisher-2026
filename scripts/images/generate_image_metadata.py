#!/usr/bin/env python3
"""
Image Metadata Generator for Camp Lakota
Generates professional metadata for images based on visual analysis
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class MetadataGenerator:
    def __init__(self, batch_file: str):
        self.batch_file = batch_file
        self.generated_metadata = []
        
    def load_batch(self):
        """Load the batch file"""
        with open(self.batch_file, 'r') as f:
            return json.load(f)
    
    def generate_metadata_for_image(self, image_data: Dict) -> Dict:
        """
        Generate metadata for a single image
        This will be called manually - the AI will view each image and generate metadata
        """
        metadata = {
            'id': image_data['id'],
            'url': image_data['url'],
            'local_path': image_data['local_path'],
            'current_title': image_data['current_title'],
            
            # These will be filled in by AI analysis
            'new_title': '',
            'alt_text': '',
            'caption': '',
            'description': '',
            'suggested_filename': '',
            'keywords': []
        }
        
        return metadata
    
    def save_metadata_csv(self, metadata_list: List[Dict], output_file: str = None):
        """Save generated metadata to CSV for review"""
        if output_file is None:
            output_file = 'image_metadata_generated.csv'
        
        fieldnames = [
            'id', 'current_title', 'new_title', 'alt_text', 
            'caption', 'description', 'suggested_filename', 
            'keywords', 'url', 'local_path'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in metadata_list:
                # Convert keywords list to string
                item_copy = item.copy()
                item_copy['keywords'] = ', '.join(item_copy.get('keywords', []))
                writer.writerow(item_copy)
        
        console.print(f"[green]✓[/green] Metadata saved to: {output_file}")
        return output_file
    
    def save_metadata_json(self, metadata_list: List[Dict], output_file: str = None):
        """Save generated metadata to JSON"""
        if output_file is None:
            output_file = 'image_metadata_generated.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✓[/green] Metadata saved to: {output_file}")
        return output_file
    
    def display_metadata_preview(self, metadata_list: List[Dict]):
        """Display preview of generated metadata"""
        table = Table(title="Generated Metadata Preview")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("New Title", style="green", width=40)
        table.add_column("Alt Text", style="yellow", width=50)
        
        for item in metadata_list[:10]:
            table.add_row(
                str(item['id']),
                item['new_title'][:40],
                item['alt_text'][:50]
            )
        
        if len(metadata_list) > 10:
            table.add_row("...", f"...and {len(metadata_list) - 10} more", "")
        
        console.print(table)


def create_example_metadata():
    """
    Example showing what good metadata looks like
    Based on the successful DSC03139 test case
    """
    example = {
        'id': 2705,
        'current_title': 'DSC03139',
        'new_title': 'Camp Lakota CIT Counselors in Training Group Photo',
        'alt_text': 'Camp Lakota CIT counselors in training posing together on the sandy beach at Masten Lake during summer camp',
        'caption': 'Our CIT (Counselors in Training) program develops teenage leadership skills through hands-on mentorship and responsibility at Camp Lakota.',
        'description': 'Counselors in Training (CIT) group photo at Camp Lakota\'s Masten Lake waterfront. Our CIT program gives older campers leadership experience, teaching them valuable skills in mentorship, responsibility, and working with children while enjoying their final summers at camp.',
        'suggested_filename': 'camp-lakota-cit-counselors-in-training-masten-lake-beach.jpg',
        'keywords': [
            'CIT program',
            'Counselors in training',
            'Camp Lakota staff',
            'Teen leadership',
            'Masten Lake',
            'Summer camp counselors',
            'Youth leadership development'
        ]
    }
    
    return example


def main():
    console.print(Panel.fit(
        "[bold cyan]Camp Lakota Image Metadata Generator[/bold cyan]\n"
        "[dim]Step 2: Generate professional metadata for downloaded images[/dim]",
        border_style="cyan"
    ))
    
    # Show example of good metadata
    console.print("\n[bold]Example of Good Metadata (from our DSC03139 test):[/bold]\n")
    example = create_example_metadata()
    
    console.print(f"[cyan]Image ID:[/cyan] {example['id']}")
    console.print(f"[cyan]Old Title:[/cyan] {example['current_title']}")
    console.print(f"[cyan]New Title:[/cyan] {example['new_title']}")
    console.print(f"[cyan]Alt Text:[/cyan] {example['alt_text']}")
    console.print(f"[cyan]Caption:[/cyan] {example['caption']}")
    console.print(f"[cyan]Suggested Filename:[/cyan] {example['suggested_filename']}")
    console.print(f"[cyan]Keywords:[/cyan] {', '.join(example['keywords'])}")
    
    console.print("\n[yellow]This script prepares the structure for metadata generation.[/yellow]")
    console.print("[yellow]The actual metadata will be generated by viewing each image.[/yellow]")
    
    # Check for batch file
    batch_files = list(Path('.').glob('image_batch_*_for_analysis.json'))
    
    if batch_files:
        console.print(f"\n[green]Found {len(batch_files)} batch file(s) ready for processing[/green]")
        for bf in batch_files:
            console.print(f"  • {bf}")
    else:
        console.print("\n[yellow]No batch files found. Run analyze_images.py first.[/yellow]")


if __name__ == "__main__":
    main()
