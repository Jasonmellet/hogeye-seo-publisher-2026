#!/usr/bin/env python3
"""
Proper Image Processing - View Each Image and Generate Specific Metadata
This script helps coordinate the workflow but the actual viewing/analysis 
happens through the AI assistant viewing images in browser
"""

import json
from pathlib import Path

# Work directory (keeps repo root clean)
WORK_DIR = Path("work") / "image-metadata"

# Load images to process
source_file = WORK_DIR / "images_to_process.json"
if not source_file.exists():
    source_file = Path("images_to_process.json")  # legacy location
with open(source_file, 'r', encoding="utf-8") as f:
    all_images = json.load(f)

# Load any existing progress
progress_file = WORK_DIR / 'image_processing_progress.json'
if progress_file.exists():
    with open(progress_file, 'r', encoding="utf-8") as f:
        processed_metadata = json.load(f)
    print(f"Resuming: {len(processed_metadata)} images already processed")
else:
    processed_metadata = []
    print(f"Starting fresh: {len(all_images)} images to process")

# Calculate remaining
processed_ids = {m['id'] for m in processed_metadata}
remaining_images = [img for img in all_images if img['id'] not in processed_ids]

print(f"\nTotal: {len(all_images)} images")
print(f"Completed: {len(processed_metadata)} images") 
print(f"Remaining: {len(remaining_images)} images")

if remaining_images:
    print(f"\nNext batch (first 15):")
    for i, img in enumerate(remaining_images[:15], 1):
        print(f"  {i}. ID {img['id']}: {img['url']}")
else:
    print("\n✓ ALL IMAGES PROCESSED!")

# Export current status
status = {
    'total': len(all_images),
    'completed': len(processed_metadata),
    'remaining': len(remaining_images),
    'next_batch': remaining_images[:15] if remaining_images else []
}

WORK_DIR.mkdir(parents=True, exist_ok=True)
with open(WORK_DIR / 'processing_status.json', 'w', encoding="utf-8") as f:
    json.dump(status, f, indent=2)

print(f"\nStatus saved to: {WORK_DIR / 'processing_status.json'}")
