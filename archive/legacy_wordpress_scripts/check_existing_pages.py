#!/usr/bin/env python3
"""
Check which pages already exist in WordPress before processing
"""

from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.table import Table
import json
import os
import re

console = Console()

auth = WordPressAuth()
session = auth.get_session()

# Get all pages from content directory
content_dir = 'content/pages'
page_files = [f for f in os.listdir(content_dir) if f.endswith('.json') and f != 'example-page.json']

console.print("\n[bold cyan]Checking Existing Pages in WordPress...[/bold cyan]\n")

table = Table()
table.add_column("Page File", style="cyan")
table.add_column("Slug", style="yellow")
table.add_column("Exists in WP", style="green")
table.add_column("WP ID", style="dim")
table.add_column("WP Status", style="dim")
table.add_column("Action", style="magenta")

for page_file in sorted(page_files):
    file_path = os.path.join(content_dir, page_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Fix JSON issues
        file_content = file_content.replace('"', '"').replace('"', '"')
        file_content = file_content.replace(''', "'").replace(''', "'")
        
        try:
            data = json.loads(file_content)
        except:
            # Extract slug manually
            slug_match = re.search(r'"slug":\s*"([^"]+)"', file_content)
            data = {'slug': slug_match.group(1) if slug_match else 'unknown'}
        
        slug = data.get('slug', 'unknown')
        
        # Check if page exists - try multiple methods
        found = False
        wp_id = "N/A"
        wp_status = "N/A"
        
        # Method 1: Search by slug
        response = session.get(
            Config.get_api_url('pages'),
            params={'slug': slug, 'per_page': 100, 'status': 'any'},
            timeout=30
        )
        
        if response.status_code == 200:
            pages = response.json()
            # Filter by exact slug match (API might return partial matches)
            for page in pages:
                if page.get('slug') == slug:
                    wp_id = page['id']
                    wp_status = page.get('status', 'unknown')
                    found = True
                    break
        
        if found:
            exists = "✅ YES"
            action = "UPDATE"
        else:
            exists = "❌ NO"
            action = "CREATE"
        
        table.add_row(page_file, slug, exists, str(wp_id), wp_status, action)
        
    except Exception as e:
        table.add_row(page_file, "Error", "❌", "N/A", "N/A", f"Error: {str(e)[:30]}")

console.print(table)

console.print("\n[bold]Summary:[/bold]")
console.print("  • Pages marked 'UPDATE' already exist and will be modified")
console.print("  • Pages marked 'CREATE' will be created as new pages")
console.print("  • Always check this before running rebuild scripts!")
