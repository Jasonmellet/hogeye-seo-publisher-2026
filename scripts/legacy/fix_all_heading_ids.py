#!/usr/bin/env python3
"""
Fix All Heading IDs for Table of Contents
Ensures all H2 headings have anchor IDs for TOC navigation.
"""

import re
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

POST_ID = 2698

def create_slug(text: str) -> str:
    """Create URL-friendly slug from heading text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def add_ids_to_headings(content: str) -> str:
    """Add IDs to all H2 headings that don't have them."""
    updated = content
    
    # Find all H2 headings
    h2_pattern = r'(<h2)([^>]*>)(.*?)(</h2>)'
    
    def replace_heading(match):
        opening = match.group(1)  # <h2
        attributes = match.group(2)  # [attributes]>
        heading_text = match.group(3)
        closing = match.group(4)  # </h2>
        
        # Check if ID already exists
        if 'id=' in attributes:
            return match.group(0)  # No change needed
        
        # Create slug
        clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
        slug = create_slug(clean_heading)
        
        # Add ID attribute
        if attributes.strip() == '>':
            # No existing attributes
            new_attributes = f' id="{slug}">'
        else:
            # Has existing attributes, add ID
            new_attributes = attributes.rstrip('>') + f' id="{slug}">'
        
        return opening + new_attributes + heading_text + closing
    
    updated = re.sub(h2_pattern, replace_heading, updated)
    
    return updated

def main():
    console.print(Panel.fit(
        "[bold yellow]Fix All Heading IDs[/bold yellow]",
        border_style="yellow"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Get post
    response = session.get(
        Config.get_api_url(f'posts/{POST_ID}'),
        params={'context': 'edit'},
        timeout=30
    )
    
    if response.status_code != 200:
        console.print(f"[red]✗ Error fetching post {POST_ID}[/red]")
        return
    
    post = response.json()
    content = post.get('content', {}).get('raw', '')
    
    # Count headings before
    h2s_before = len(re.findall(r'<h2[^>]*>', content))
    h2s_with_ids_before = len(re.findall(r'<h2[^>]*id="[^"]*"', content))
    
    console.print(f"\n[cyan]Before:[/cyan] {h2s_with_ids_before} / {h2s_before} headings have IDs")
    
    # Add IDs to all headings
    updated_content = add_ids_to_headings(content)
    
    # Count after
    h2s_with_ids_after = len(re.findall(r'<h2[^>]*id="[^"]*"', updated_content))
    
    console.print(f"[cyan]After:[/cyan] {h2s_with_ids_after} / {h2s_before} headings have IDs")
    
    if updated_content != content:
        # Update post
        update_response = session.post(
            Config.get_api_url(f'posts/{POST_ID}'),
            json={'content': updated_content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            console.print(f"\n[green]✓ Added IDs to {h2s_with_ids_after - h2s_with_ids_before} headings[/green]")
            console.print(f"[green]✓ All {h2s_before} headings now have anchor IDs[/green]")
        else:
            console.print(f"\n[red]✗ Error updating: {update_response.status_code}[/red]")
    else:
        console.print(f"\n[green]✓ All headings already have IDs[/green]")

if __name__ == '__main__':
    main()
