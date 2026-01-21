#!/usr/bin/env python3
"""
Agent 4 Image Metadata Processor
Processes List 4 of unprocessed WordPress Media images and updates metadata.
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
PART4_CSV = Path(__file__).parent / 'image_remaining_unprocessed_part4.csv'


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
    """
    Update WordPress media metadata via API
    
    Args:
        image_id: WordPress media ID
        metadata: Dict with title, alt_text, caption, description
        session: Authenticated requests session
    
    Returns:
        True if successful, False otherwise
    """
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
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating image {image_id}: {e}")
        return False


def print_image_info(image: Dict):
    """Print image information"""
    print("\n" + "=" * 80)
    print(f"Image ID: {image['id']}")
    print(f"Current Title: {image.get('title', 'N/A')}")
    print(f"Source URL: {image['source_url']}")
    print(f"WordPress Edit URL: https://www.camplakota.com/wp-admin/post.php?post={image['id']}&action=edit")
    print("=" * 80)


def main():
    """Main processing function"""
    print("Agent 4 Image Metadata Processor")
    print("=" * 80)
    
    # Load images
    images = load_part4_images()
    done_ids = load_done_ids()
    
    # Filter out already processed images
    remaining = [img for img in images if img['id'] not in done_ids]
    
    print(f"\nTotal images in part4: {len(images)}")
    print(f"Already processed: {len(done_ids)}")
    print(f"Remaining to process: {len(remaining)}")
    
    if not remaining:
        print("\n✅ All images in part4 have been processed!")
        return
    
    # Initialize WordPress connection
    print("\nConnecting to WordPress...")
    auth = WordPressAuth()
    session = auth.get_session()
    
    # Test connection
    success, message, data = auth.test_connection()
    if not success:
        print(f"❌ Connection failed: {message}")
        return
    
    print(f"✅ {message}")
    if data:
        print(f"   Site: {data.get('site_name', 'Unknown')}")
        print(f"   User: {data.get('user_name', 'Unknown')}")
    
    # Process images
    print(f"\n{'='*80}")
    print("Starting image processing...")
    print("Instructions:")
    print("1. Each image will be opened in a browser")
    print("2. Review the image and generate metadata")
    print("3. Metadata will be updated in WordPress")
    print("4. Progress will be tracked automatically")
    print(f"{'='*80}\n")
    
    for idx, image in enumerate(remaining, 1):
        print_image_info(image)
        print(f"\nProcessing image {idx}/{len(remaining)}")
        print(f"Opening image in browser: {image['source_url']}")
        
        # Note: The actual browser opening and metadata generation
        # will be done interactively by the AI assistant
        # This script provides the framework for batch processing
        
        print("\n⏸️  Ready for metadata generation and update")
        print("   (This will be handled by the AI assistant viewing the image)")
        
        # Placeholder for metadata - will be filled by AI assistant
        # metadata = {
        #     'title': '...',
        #     'alt_text': '...',
        #     'caption': '...',
        #     'description': '...'
        # }
        
        # Uncomment when ready to update:
        # if update_wordpress_metadata(image['id'], metadata, session):
        #     save_done_id(image['id'])
        #     print(f"✅ Completed image {image['id']}")
        # else:
        #     print(f"❌ Failed to update image {image['id']}")
        
        print()


if __name__ == '__main__':
    main()
