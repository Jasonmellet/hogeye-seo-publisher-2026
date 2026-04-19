"""
Image Upload Module
Handles image uploads and metadata management
"""

import mimetypes
from pathlib import Path
from typing import Dict, Optional
from config import Config


class ImageUploader:
    """Handle image uploads to WordPress media library"""
    
    def __init__(self, session):
        """
        Initialize image uploader
        Args:
            session: Authenticated requests session
        """
        self.session = session
        self.images_dir = Config.IMAGES_DIR
        self.uploaded_images = {}  # Track uploaded images {filename: media_id}
    
    def get_image_path(self, filename: str) -> Optional[Path]:
        """Get full path to image file"""
        image_path = self.images_dir / filename
        
        if not image_path.exists():
            print(f"⚠️  Image not found: {filename}")
            return None
        
        return image_path
    
    def upload_image(self, filename: str, metadata: Optional[Dict] = None) -> Optional[int]:
        """
        Upload image to WordPress media library
        
        Args:
            filename: Name of image file
            metadata: Optional dict with alt_text, title, caption, description
        
        Returns:
            Media ID if successful, None otherwise
        """
        # Check if already uploaded
        if filename in self.uploaded_images:
            print(f"ℹ️  Image already uploaded: {filename}")
            return self.uploaded_images[filename]
        
        image_path = self.get_image_path(filename)
        if not image_path:
            return None
        
        try:
            # Determine mime type
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type:
                mime_type = 'image/jpeg'  # Default
            
            # Read image file
            with open(image_path, 'rb') as img_file:
                files = {
                    'file': (filename, img_file, mime_type)
                }
                
                # Upload image
                response = self.session.post(
                    Config.get_api_url('media'),
                    files=files,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                media_data = response.json()
                media_id = media_data['id']
                
                # Update metadata if provided
                if metadata:
                    self.update_image_metadata(media_id, metadata)
                
                # Cache the media ID
                self.uploaded_images[filename] = media_id
                
                print(f"✅ Uploaded image: {filename} (ID: {media_id})")
                return media_id
            else:
                print(f"❌ Failed to upload {filename}: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return None
    
    def update_image_metadata(self, media_id: int, metadata: Dict) -> bool:
        """
        Update metadata for uploaded image
        
        Args:
            media_id: WordPress media ID
            metadata: Dict with alt_text, title, caption, description
        
        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {}
            
            if metadata.get('alt_text'):
                update_data['alt_text'] = metadata['alt_text']
            
            if metadata.get('title'):
                update_data['title'] = metadata['title']
            
            if metadata.get('caption'):
                update_data['caption'] = metadata['caption']
            
            if metadata.get('description'):
                update_data['description'] = metadata['description']
            
            if not update_data:
                return True  # Nothing to update
            
            response = self.session.post(
                Config.get_api_url(f'media/{media_id}'),
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Updated metadata for media ID: {media_id}")
                return True
            else:
                print(f"⚠️  Failed to update metadata for media ID {media_id}: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Error updating metadata for media ID {media_id}: {e}")
            return False
    
    def upload_multiple_images(self, image_list: list) -> Dict[str, int]:
        """
        Upload multiple images
        
        Args:
            image_list: List of dicts with 'filename' and optional metadata
        
        Returns:
            Dict mapping filename to media_id
        """
        results = {}
        
        for image_info in image_list:
            filename = image_info.get('filename')
            if not filename:
                continue
            
            metadata = {
                'alt_text': image_info.get('alt_text', ''),
                'title': image_info.get('title', ''),
                'caption': image_info.get('caption', ''),
                'description': image_info.get('description', '')
            }
            
            media_id = self.upload_image(filename, metadata)
            if media_id:
                results[filename] = media_id
        
        return results
    
    def get_uploaded_image_id(self, filename: str) -> Optional[int]:
        """Get media ID for previously uploaded image"""
        return self.uploaded_images.get(filename)
