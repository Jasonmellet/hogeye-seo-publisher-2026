#!/usr/bin/env python3
"""
Update a single Agent 4 image metadata
"""

import sys
from modules.auth import WordPressAuth
from config import Config

def update_image_metadata(image_id: int, metadata: dict):
    """Update WordPress image metadata"""
    auth = WordPressAuth()
    session = auth.get_session()
    
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
    
    try:
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
    if len(sys.argv) < 2:
        print("Usage: python update_agent4_image.py <image_id>")
        sys.exit(1)
    
    image_id = int(sys.argv[1])
    
    # Metadata will be provided as needed
    metadata = {
        'title': '',
        'alt_text': '',
        'caption': '',
        'description': ''
    }
    
    update_image_metadata(image_id, metadata)
