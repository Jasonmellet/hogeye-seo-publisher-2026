#!/usr/bin/env python3
"""
Update Agent 3 images with metadata
"""

import json
from pathlib import Path
from modules.auth import WordPressAuth
from config import Config

def update_image_metadata(image_id: int, metadata: dict, session):
    """Update WordPress image metadata"""
    update_data = {
        'title': metadata.get('title', ''),
        'alt_text': metadata.get('alt_text', ''),
        'caption': metadata.get('caption', ''),
        'description': metadata.get('description', '')
    }
    
    # Remove empty fields
    update_data = {k: v for k, v in update_data.items() if v}
    
    if not update_data:
        print(f"⚠️  No metadata to update for image {image_id}")
        return False
    
    try:
        media_url = Config.get_api_url(f'media/{image_id}')
        response = session.post(
            media_url,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Updated image {image_id}: {metadata.get('title', '')[:50]}")
            return True
        else:
            print(f"❌ Failed to update image {image_id}: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error updating image {image_id}: {e}")
        return False

def main():
    # Load metadata
    metadata_file = Path(__file__).parent / 'agent3_metadata_updates.json'
    if not metadata_file.exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        return
    
    with open(metadata_file, 'r') as f:
        metadata_list = json.load(f)
    
    # Connect to WordPress
    auth = WordPressAuth()
    session = auth.get_session()
    
    success, message, _ = auth.test_connection()
    if not success:
        print(f"❌ Connection failed: {message}")
        return
    
    print(f"✅ {message}\n")
    
    # Update images
    for metadata in metadata_list:
        update_image_metadata(metadata['id'], metadata, session)

if __name__ == '__main__':
    main()
