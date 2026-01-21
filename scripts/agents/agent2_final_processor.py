#!/usr/bin/env python3
"""
Agent 2: Final Batch Processor for Remaining Images
Processes all remaining images from List 2
"""

import json
from pathlib import Path
from modules.auth import WordPressAuth
from config import Config

# Prefer work/ paths (clean root), but keep legacy fallback.
WORK_AGENTS_DIR = Path("work") / "agents"
WORK_IMAGE_INPUTS_DIR = Path("work") / "image-metadata" / "inputs"


def _pick_existing_path(*candidates: Path) -> Path:
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

# Load images
input_file = _pick_existing_path(
    WORK_IMAGE_INPUTS_DIR / "image_remaining_unprocessed_part2.json",
    Path("image_remaining_unprocessed_part2.json"),  # legacy root location
)
with open(input_file, 'r', encoding="utf-8") as f:
    all_images = json.load(f)

# Load processed IDs
processed = set()
tracking_file = _pick_existing_path(
    WORK_AGENTS_DIR / "agent2_done_ids.txt",
    Path("agent2_done_ids.txt"),  # legacy root location
)
if tracking_file.exists():
    with open(tracking_file, 'r', encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                processed.add(int(line.strip()))

# Get remaining
remaining = [img for img in all_images if img['id'] not in processed]
print(f"Processing {len(remaining)} remaining images...\n")

# Authenticate
auth = WordPressAuth()
session = auth.get_session()

# Metadata dictionary - will be populated as we view images
# For now, this is a placeholder structure
METADATA = {}

def update_image(image_id: int, metadata: dict) -> bool:
    """Update WordPress image"""
    try:
        media_url = f"{Config.get_api_url('media')}/{image_id}"
        response = session.post(media_url, json=metadata, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error updating {image_id}: {e}")
        return False

def save_tracking(image_id: int):
    """Save processed ID"""
    WORK_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(tracking_file, 'a', encoding="utf-8") as f:
        f.write(f"{image_id}\n")

# Process images that have metadata
success = 0
failed = 0

for image in remaining:
    image_id = image['id']
    
    if image_id in METADATA:
        metadata = METADATA[image_id]
        if update_image(image_id, metadata):
            save_tracking(image_id)
            print(f"✓ Updated {image_id}: {metadata['title']}")
            success += 1
        else:
            print(f"✗ Failed {image_id}")
            failed += 1
    else:
        print(f"⊝ No metadata yet for {image_id}: {image['title']}")

print(f"\nSummary: {success} success, {failed} failed")
print(f"Remaining without metadata: {len(remaining) - success - failed}")
