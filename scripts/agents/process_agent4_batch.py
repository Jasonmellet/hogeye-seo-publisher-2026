#!/usr/bin/env python3
"""
Agent 4 Batch Image Metadata Processor
Processes List 4 images by viewing each in browser and updating WordPress metadata.
"""

import json
from pathlib import Path
from typing import Dict, List
from modules.auth import WordPressAuth
from config import Config

# Tracking files
WORK_AGENTS_DIR = Path("work") / "agents"
DONE_IDS_FILE = WORK_AGENTS_DIR / "agent4_done_ids.txt"
QUESTIONS_FILE = Path(__file__).parent / 'agent4_questions.txt'

# Input files
PART4_JSON = Path(__file__).parent / 'image_remaining_unprocessed_part4.json'


def load_done_ids() -> set:
    """Load already processed image IDs"""
    if DONE_IDS_FILE.exists():
        with open(DONE_IDS_FILE, 'r') as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}
    return set()


def save_done_id(image_id: int):
    """Save a completed image ID"""
    with open(DONE_IDS_FILE, 'a') as f:
        f.write(f"{image_id}\n")


def save_question(image_id: int, source_url: str, question: str):
    """Save a question about an image"""
    with open(QUESTIONS_FILE, 'a') as f:
        f.write(f"ID: {image_id}\n")
        f.write(f"URL: {source_url}\n")
        f.write(f"Question: {question}\n")
        f.write("-" * 80 + "\n\n")


def load_part4_images() -> List[Dict]:
    """Load images from part4 JSON file"""
    with open(PART4_JSON, 'r') as f:
        return json.load(f)


def update_wordpress_metadata(image_id: int, metadata: Dict, session) -> bool:
    """Update WordPress media metadata via API"""
    try:
        update_data = {}
        
        if metadata.get('title'):
            update_data['title'] = metadata['title']
        
        if metadata.get('alt_text'):
            update_data['alt_text'] = metadata['alt_text']
        
        if metadata.get('caption'):
            update_data['caption'] = metadata['caption']
        
        if metadata.get('description'):
            update_data['description'] = metadata['description']
        
        if not update_data:
            print(f"⚠️  No metadata to update for image {image_id}")
            return False
        
        media_url = Config.get_api_url(f'media/{image_id}')
        response = session.post(
            media_url,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Updated metadata for image ID: {image_id}")
            return True
        else:
            print(f"❌ Failed to update image {image_id}: HTTP {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating image {image_id}: {e}")
        return False


if __name__ == '__main__':
    # This script will be used by the AI assistant to process images
    # The actual processing will happen interactively
    print("Agent 4 Image Processor - Ready for batch processing")
