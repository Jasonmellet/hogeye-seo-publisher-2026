#!/usr/bin/env python3
"""
Bulk Image Metadata Processor for Camp Lakota
Processes ALL images in parallel batches for maximum speed
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table

from modules.auth import WordPressAuth
from config import Config

console = Console()

class BulkImageProcessor:
    def __init__(self, max_workers=5):
        self.auth = WordPressAuth()
        self.session = self.auth.get_session()
        self.max_workers = max_workers
        self.results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
    def fetch_all_images_needing_metadata(self):
        """Fetch ALL images missing metadata from WordPress"""
        console.print("\n[cyan]Fetching all images from WordPress...[/cyan]")
        
        all_media = []
        page = 1
        per_page = 100
        
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
            console.print(f"[dim]Loaded {len(all_media)} images...[/dim]")
            page += 1
        
        # Filter for images missing metadata
        needs_metadata = []
        for img in all_media:
            has_alt = bool(img.get('alt_text', '').strip())
            has_caption = bool(img.get('caption', {}).get('rendered', '').strip())
            title_is_generic = (
                img['title']['rendered'].startswith('DSC') or 
                img['title']['rendered'].startswith('IMG') or 
                img['title']['rendered'].startswith('_') or
                img['title']['rendered'].startswith('image')
            )
            
            if not has_alt or not has_caption or title_is_generic:
                needs_metadata.append({
                    'id': img['id'],
                    'title': img['title']['rendered'],
                    'url': img['source_url'],
                    'alt_text': img.get('alt_text', ''),
                    'caption': img.get('caption', {}).get('rendered', '')
                })
        
        console.print(f"[green]✓[/green] Found {len(all_media)} total images")
        console.print(f"[yellow]⚠[/yellow] {len(needs_metadata)} need metadata")
        
        return needs_metadata
    
    def update_single_image(self, image_data: Dict, metadata: Dict) -> bool:
        """Update a single image in WordPress"""
        image_id = image_data['id']
        media_url = f"{Config.get_api_url('media')}/{image_id}"
        
        update_data = {
            'title': metadata['title'],
            'alt_text': metadata['alt_text'],
            'caption': metadata['caption'],
            'description': metadata['description']
        }
        
        try:
            response = self.session.post(media_url, json=update_data, timeout=30)
            
            if response.status_code == 200:
                self.results['success'].append({
                    'id': image_id,
                    'title': metadata['title'][:50]
                })
                return True
            else:
                self.results['failed'].append({
                    'id': image_id,
                    'error': f"HTTP {response.status_code}"
                })
                return False
                
        except Exception as e:
            self.results['failed'].append({
                'id': image_id,
                'error': str(e)[:100]
            })
            return False
    
    def update_images_parallel(self, updates: List[tuple]):
        """Update multiple images in parallel"""
        console.print(f"\n[cyan]Updating {len(updates)} images with {self.max_workers} parallel workers...[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Updating WordPress...", total=len(updates))
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.update_single_image, img_data, metadata): (img_data, metadata)
                    for img_data, metadata in updates
                }
                
                for future in as_completed(futures):
                    img_data, metadata = futures[future]
                    try:
                        success = future.result()
                        if success:
                            console.print(f"[green]✓[/green] {img_data['id']}: {metadata['title'][:60]}")
                    except Exception as e:
                        console.print(f"[red]✗[/red] {img_data['id']}: Error - {str(e)[:60]}")
                    
                    progress.update(task, advance=1)
    
    def display_results(self):
        """Display final results"""
        console.print("\n" + "="*80)
        console.print(Panel.fit(
            f"[bold green]Bulk Processing Complete![/bold green]\n\n"
            f"[green]✓ Successfully updated: {len(self.results['success'])}[/green]\n"
            f"[red]✗ Failed: {len(self.results['failed'])}[/red]\n"
            f"[yellow]⊝ Skipped: {len(self.results['skipped'])}[/yellow]",
            border_style="green"
        ))
        
        if self.results['failed']:
            console.print("\n[bold red]Failed Updates:[/bold red]")
            for item in self.results['failed'][:20]:  # Show first 20
                console.print(f"  ID {item['id']}: {item['error']}")
            if len(self.results['failed']) > 20:
                console.print(f"  ... and {len(self.results['failed']) - 20} more")


def generate_metadata_from_url(image_data: Dict) -> Dict:
    """
    Generate metadata based on image URL patterns and existing data
    This is a fast heuristic-based approach while we wait for AI analysis
    """
    url = image_data['url'].lower()
    title = image_data['title']
    
    # Common patterns in camp photos
    if 'horse' in url or 'equestrian' in url or 'riding' in url:
        return {
            'title': f"Camp Lakota Horseback Riding Activity - {title}",
            'alt_text': "Camp Lakota camper enjoying horseback riding program with professional instruction and safety supervision",
            'caption': "Our horseback riding program teaches responsibility, confidence, and animal care under experienced equestrian guidance.",
            'description': "Camp Lakota's horseback riding program offers supervised equestrian activities where campers learn riding skills, horse care, and safety while building confidence in a supportive environment."
        }
    elif 'water' in url or 'lake' in url or 'swim' in url or 'kayak' in url or 'boat' in url:
        return {
            'title': f"Camp Lakota Waterfront Activities at Masten Lake - {title}",
            'alt_text': "Camp Lakota campers enjoying waterfront activities and water sports at Masten Lake",
            'caption': "Masten Lake provides the perfect setting for swimming, boating, and water sports with certified lifeguard supervision.",
            'description': "Camp Lakota's waterfront program on Masten Lake offers diverse water activities including swimming, kayaking, canoeing, and water sports, all supervised by certified lifeguards and experienced waterfront staff."
        }
    elif 'art' in url or 'craft' in url or 'paint' in url or 'pottery' in url:
        return {
            'title': f"Camp Lakota Arts and Crafts Creative Activity - {title}",
            'alt_text': "Camp Lakota campers engaged in creative arts and crafts activity with counselor guidance",
            'caption': "Our arts and crafts program encourages creativity and self-expression through hands-on projects and artistic exploration.",
            'description': "Camp Lakota's comprehensive arts program includes painting, pottery, crafts, and mixed media projects that allow campers to explore creativity and develop new skills in a supportive environment."
        }
    elif 'sport' in url or 'soccer' in url or 'basketball' in url or 'volleyball' in url:
        return {
            'title': f"Camp Lakota Team Sports and Athletic Activities - {title}",
            'alt_text': "Camp Lakota campers participating in team sports and athletic activities on camp fields",
            'caption': "Team sports at Camp Lakota teach cooperation, sportsmanship, and athletic skills in a fun, supportive environment.",
            'description': "Camp Lakota offers diverse sports including soccer, basketball, volleyball, and more, where campers develop athletic skills, teamwork, and confidence through friendly competition and expert coaching."
        }
    elif 'campfire' in url or 'fire' in url or 'sing' in url:
        return {
            'title': f"Camp Lakota Campfire and Evening Programs - {title}",
            'alt_text': "Camp Lakota campers gathered around campfire for songs and traditions at evening program",
            'caption': "Campfire gatherings create magical moments and lasting memories through songs, stories, and camp traditions.",
            'description': "Camp Lakota's evening campfire programs bring the community together for singing, storytelling, and cherished traditions that create powerful bonds and unforgettable summer memories."
        }
    elif 'archery' in url or 'arrow' in url or 'bow' in url:
        return {
            'title': f"Camp Lakota Archery Program and Instruction - {title}",
            'alt_text': "Camp Lakota camper learning archery skills with certified instructor on dedicated archery range",
            'caption': "Our archery program teaches focus, patience, and skill development under certified instructor guidance.",
            'description': "Camp Lakota's archery program offers professional instruction on our dedicated range, where campers learn proper technique, safety, and develop confidence through progressive skill building."
        }
    elif 'climb' in url or 'ropes' in url or 'adventure' in url:
        return {
            'title': f"Camp Lakota Adventure and Ropes Course Activities - {title}",
            'alt_text': "Camp Lakota camper on ropes course or adventure challenge activity with safety equipment",
            'caption': "Our adventure programs challenge campers to push boundaries and build confidence through supervised outdoor activities.",
            'description': "Camp Lakota's ropes course and adventure activities provide thrilling challenges that help campers overcome fears, build confidence, and develop problem-solving skills in a safe, supervised environment."
        }
    elif 'cit' in url.lower() or 'counselor' in url or 'staff' in url:
        return {
            'title': f"Camp Lakota CIT and Staff Programs - {title}",
            'alt_text': "Camp Lakota CIT counselors in training and staff members during summer camp program",
            'caption': "Our CIT program develops teenage leadership skills through mentorship, responsibility, and hands-on experience.",
            'description': "Camp Lakota's Counselors in Training (CIT) program gives older campers leadership experience, teaching valuable skills in mentorship and working with children while enjoying their final summers at camp."
        }
    elif 'dining' in url or 'food' in url or 'meal' in url:
        return {
            'title': f"Camp Lakota Dining Hall and Meal Times - {title}",
            'alt_text': "Camp Lakota campers enjoying family-style meals together in dining hall",
            'caption': "Family-style meals bring our camp community together three times daily for nutrition, conversation, and connection.",
            'description': "Camp Lakota's dining program provides nutritious, varied meals in a communal setting where campers bond over food, celebrate together, and accommodate all dietary needs and preferences."
        }
    elif 'cabin' in url or 'bunk' in url:
        return {
            'title': f"Camp Lakota Cabin Life and Living Arrangements - {title}",
            'alt_text': "Camp Lakota cabin bunks and living space where campers build friendships and community",
            'caption': "Cabin life creates close bonds as campers live, play, and grow together throughout the summer session.",
            'description': "Camp Lakota cabins provide comfortable, supervised living spaces where campers develop independence, build lasting friendships, and learn to live cooperatively in a structured community."
        }
    else:
        # Generic camp activity
        return {
            'title': f"Camp Lakota Summer Camp Activities and Programs - {title}",
            'alt_text': "Camp Lakota campers participating in summer camp activities and programs",
            'caption': "Camp Lakota offers diverse activities that help campers build confidence, make friends, and create lasting memories.",
            'description': "At Camp Lakota, campers enjoy a wide range of activities including sports, arts, waterfront fun, and special events, all designed to foster growth, friendship, and unforgettable summer experiences on our beautiful Wurtsboro campus."
        }


def main():
    console.print(Panel.fit(
        "[bold cyan]Camp Lakota Bulk Image Processor[/bold cyan]\n"
        "[dim]Processing ALL images with parallel workers for maximum speed[/dim]",
        border_style="cyan"
    ))
    
    processor = BulkImageProcessor(max_workers=10)  # 10 parallel workers
    
    # Fetch all images needing metadata
    images = processor.fetch_all_images_needing_metadata()
    
    if not images:
        console.print("\n[green]✓[/green] All images have metadata!")
        return
    
    console.print(f"\n[bold yellow]Generating metadata for {len(images)} images...[/bold yellow]")
    
    # Generate metadata for all images
    updates = []
    for image_data in images:
        metadata = generate_metadata_from_url(image_data)
        updates.append((image_data, metadata))
    
    console.print(f"[green]✓[/green] Generated metadata for {len(updates)} images")
    
    # Update WordPress in parallel
    start_time = time.time()
    processor.update_images_parallel(updates)
    elapsed = time.time() - start_time
    
    # Display results
    processor.display_results()
    
    console.print(f"\n[cyan]⏱️  Total time: {elapsed:.1f} seconds[/cyan]")
    console.print(f"[cyan]📊 Average: {elapsed/len(images):.2f} seconds per image[/cyan]")
    
    # Save results
    with open('bulk_processing_results.json', 'w') as f:
        json.dump(processor.results, f, indent=2)
    
    console.print(f"\n[green]✓[/green] Results saved to: bulk_processing_results.json")


if __name__ == "__main__":
    main()
