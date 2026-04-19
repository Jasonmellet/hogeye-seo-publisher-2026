#!/usr/bin/env python3
"""
Fast Priority Image Processor
Process the 42 priority images that are actually used on the site
Creates metadata file that I'll review and refine, then update WordPress
"""

import json
from pathlib import Path

# Work directory (keeps repo root clean)
WORK_DIR = Path("work") / "image-metadata"

# Load priority images
source_file = WORK_DIR / "priority_images.json"
if not source_file.exists():
    source_file = Path("priority_images.json")  # legacy location
with open(source_file, 'r', encoding="utf-8") as f:
    priority_images = json.load(f)

# Filter to only those needing metadata
needs_metadata = [img for img in priority_images if not img['has_metadata']]

print(f"Priority Images Analysis:")
print(f"Total priority images: {len(priority_images)}")
print(f"Already have metadata: {len(priority_images) - len(needs_metadata)}")  
print(f"Need metadata: {len(needs_metadata)}\n")

print("Images needing metadata (by page usage):")
for img in needs_metadata[:10]:
    print(f"  ID {img['id']}: {img['title']}")
    print(f"    {img['url']}\n")

# This file will store metadata as I create it
output_file = WORK_DIR / 'priority_images_metadata.json'
if output_file.exists():
    with open(output_file, 'r', encoding="utf-8") as f:
        existing = json.load(f)
    print(f"\nExisting progress: {len(existing)} images already have metadata prepared")
else:
    print(f"\nReady to create metadata for all {len(needs_metadata)} images")

print(f"\nNext: AI assistant will view each image and create specific metadata")
print(f"Then: Update WordPress with 5 parallel workers for speed")
