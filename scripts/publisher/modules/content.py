"""
Content Processing Module
Handles parsing and validation of pages and posts
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from config import Config


class ContentProcessor:
    """Process and validate content files"""
    
    def __init__(self):
        self.pages_dir = Config.PAGES_DIR
        self.posts_dir = Config.POSTS_DIR
    
    def load_json_file(self, file_path: Path) -> Optional[Dict]:
        """Load and parse a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {file_path.name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
            return None
    
    def load_pages(self) -> List[Dict]:
        """Load all page content files"""
        pages = []
        
        if not self.pages_dir.exists():
            print(f"⚠️  Pages directory not found: {self.pages_dir}")
            return pages
        
        json_files = list(self.pages_dir.glob('*.json'))
        
        if not json_files:
            print(f"⚠️  No JSON files found in {self.pages_dir}")
            return pages
        
        for file_path in json_files:
            content = self.load_json_file(file_path)
            if content:
                content['_source_file'] = file_path.name
                pages.append(content)
                print(f"✅ Loaded page: {file_path.name}")
        
        return pages
    
    def load_posts(self) -> List[Dict]:
        """Load all post content files"""
        posts = []
        
        if not self.posts_dir.exists():
            print(f"⚠️  Posts directory not found: {self.posts_dir}")
            return posts
        
        json_files = list(self.posts_dir.glob('*.json'))
        
        if not json_files:
            print(f"⚠️  No JSON files found in {self.posts_dir}")
            return posts
        
        for file_path in json_files:
            content = self.load_json_file(file_path)
            if content:
                content['_source_file'] = file_path.name
                posts.append(content)
                print(f"✅ Loaded post: {file_path.name}")
        
        return posts
    
    def validate_page(self, page: Dict) -> tuple[bool, List[str]]:
        """
        Validate page content
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['title', 'content']
        
        for field in required_fields:
            if not page.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate slug if present
        if 'slug' in page and page['slug']:
            if not self._is_valid_slug(page['slug']):
                errors.append(f"Invalid slug: {page['slug']}")
        
        return len(errors) == 0, errors
    
    def validate_post(self, post: Dict) -> tuple[bool, List[str]]:
        """
        Validate post content
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['title', 'content']
        
        for field in required_fields:
            if not post.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate slug if present
        if 'slug' in post and post['slug']:
            if not self._is_valid_slug(post['slug']):
                errors.append(f"Invalid slug: {post['slug']}")
        
        return len(errors) == 0, errors
    
    def _is_valid_slug(self, slug: str) -> bool:
        """Check if slug is valid (lowercase, hyphens, no spaces)"""
        import re
        return bool(re.match(r'^[a-z0-9-]+$', slug))
    
    def prepare_page_data(self, page: Dict) -> Dict:
        """
        Prepare page data for WordPress API
        Returns: formatted data for API submission
        """
        data = {
            'title': page['title'],
            'content': page['content'],
            'status': page.get('status', 'publish'),
            'slug': page.get('slug', ''),
        }
        
        # Add meta description if provided
        if page.get('meta'):
            data['meta'] = page['meta']
        
        # Add excerpt if provided
        if page.get('excerpt'):
            data['excerpt'] = page['excerpt']
        
        # Add featured image ID if provided
        if page.get('featured_media'):
            data['featured_media'] = page['featured_media']
        
        return data
    
    def prepare_post_data(self, post: Dict) -> Dict:
        """
        Prepare post data for WordPress API
        Returns: formatted data for API submission
        """
        data = {
            'title': post['title'],
            'content': post['content'],
            'status': post.get('status', 'publish'),
            'slug': post.get('slug', ''),
        }
        
        # Add excerpt if provided
        if post.get('excerpt'):
            data['excerpt'] = post['excerpt']
        
        # Add categories if provided (IDs)
        if post.get('categories'):
            data['categories'] = post['categories']
        
        # Add tags if provided (IDs)
        if post.get('tags'):
            data['tags'] = post['tags']
        
        # Add meta if provided
        if post.get('meta'):
            data['meta'] = post['meta']
        
        # Add featured image ID if provided
        if post.get('featured_media'):
            data['featured_media'] = post['featured_media']
        
        # Add author ID if provided
        if post.get('author'):
            data['author'] = post['author']
        
        # Add publish date if provided
        if post.get('date'):
            data['date'] = post['date']
        
        return data
