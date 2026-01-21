"""
Internal Linking Module
Handles internal link mapping and insertion
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional


class InternalLinkManager:
    """Manage internal links between pages and posts"""

    def __init__(self, session, *, link_aliases: Optional[Dict[str, str]] = None):
        """
        Initialize link manager
        Args:
            session: Authenticated requests session
        """
        self.session = session
        self.slug_to_url = {}  # Map slugs to full URLs
        self.slug_to_id = {}  # Map slugs to WordPress IDs
        self.link_aliases = link_aliases or {}

    def register_published_content(self, slug: str, url: str, wp_id: int):
        """
        Register published content for linking
        """
        self.slug_to_url[slug] = url
        self.slug_to_id[slug] = wp_id
        print(f"📌 Registered: {slug} → {url}")

    def replace_link_placeholders(self, content: str, link_map: Optional[Dict] = None) -> str:
        """
        Replace link placeholders with actual URLs

        Supports formats:
        - {{link:slug}} → full URL
        - {{link:slug|anchor text}} → <a href="url">anchor text</a>
        """
        if link_map is None:
            link_map = self.slug_to_url

        # 1) Handle placeholders embedded inside href attributes:
        #    <a href="{{link:slug|Anchor}}">Anchor</a>
        #    should become <a href="https://...">Anchor</a>
        # Allow whitespace around '=' and support any attribute case (href/HREF/etc).
        href_pattern = r'href\s*=\s*(["\'])\{\{link:([^|}]+)(?:\|[^}]+)?\}\}\1'

        def replace_href(match):
            quote = match.group(1)
            slug = match.group(2).strip()
            url = link_map.get(slug)
            if not url:
                print(f"⚠️  Link placeholder not found for href: {{{{link:{slug}}}}}")
                return match.group(0)
            return f"href={quote}{url}{quote}"

        content = re.sub(href_pattern, replace_href, content, flags=re.IGNORECASE)

        # 2) Handle standalone placeholders:
        # Pattern: {{link:slug}} or {{link:slug|anchor text}}
        pattern = r"\{\{link:([^|}]+)(?:\|([^}]+))?\}\}"

        def replace_match(match):
            slug = match.group(1).strip()
            anchor_text = match.group(2).strip() if match.group(2) else None

            # Get URL for slug
            url = link_map.get(slug)

            if not url:
                print(f"⚠️  Link placeholder not found: {{{{link:{slug}}}}}")
                return match.group(0)  # Return unchanged

            # If anchor text provided, create full link
            if anchor_text:
                return f'<a href="{url}">{anchor_text}</a>'
            else:
                return url

        updated_content = re.sub(pattern, replace_match, content)
        return updated_content

    def find_link_placeholders(self, content: str) -> List[str]:
        """
        Find all link placeholders in content
        """
        pattern = r"\{\{link:([^|}]+)(?:\|[^}]+)?\}\}"
        matches = re.findall(pattern, content)
        return [slug.strip() for slug in matches]

    def update_content_links(self, wp_id: int, content_type: str, updated_content: str) -> bool:
        """
        Update WordPress content with resolved links
        """
        from agt_publisher_core.config import Config

        try:
            response = self.session.post(
                Config.get_api_url(f"{content_type}/{wp_id}"),
                json={"content": updated_content},
                timeout=10,
            )

            if response.status_code == 200:
                print(f"✅ Updated links for {content_type[:-1]} ID: {wp_id}")
                return True
            else:
                print(f"⚠️  Failed to update links for {content_type[:-1]} ID {wp_id}: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error updating links for {content_type[:-1]} ID {wp_id}: {e}")
            return False

    def process_content_links(self, content_items: List[Dict], content_type: str):
        """
        Process and update internal links for all content
        """
        print(f"\n🔗 Processing internal links for {content_type}...")

        for item in content_items:
            wp_id = item.get("id")
            content = item.get("content", "")

            if not wp_id or not content:
                continue

            # Find placeholders
            placeholders = self.find_link_placeholders(content)

            if not placeholders:
                continue

            print(f"\n📝 Processing {item.get('slug', 'unknown')}...")
            print(f"   Found {len(placeholders)} link placeholder(s)")

            # Replace placeholders
            updated_content = self.replace_link_placeholders(content)

            # Update if content changed
            if updated_content != content:
                self.update_content_links(wp_id, content_type, updated_content)
            else:
                print("   No changes needed")

    def build_slug_map(self) -> Dict[str, str]:
        """
        Build a slug -> permalink map from the current WordPress site (pages + posts).
        Centralizes the logic used by internal link resolution scripts.
        """
        from agt_publisher_core.config import Config

        slug_map: Dict[str, str] = {}
        for content_type in ["pages", "posts"]:
            page = 1
            while True:
                resp = self.session.get(
                    Config.get_api_url(content_type),
                    params={"per_page": 100, "page": page, "status": "any"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    break
                items = resp.json()
                if not items:
                    break
                for item in items:
                    slug = item.get("slug")
                    link = item.get("link")
                    if slug and link:
                        slug_map[slug] = link
                page += 1

        # Optional per-client aliases (committed in client.config.json)
        for k, v in (self.link_aliases or {}).items():
            if k and v and k not in slug_map:
                slug_map[k] = v

        return slug_map

    def get_url_for_slug(self, slug: str) -> Optional[str]:
        """Get URL for a given slug"""
        return self.slug_to_url.get(slug)

    def get_id_for_slug(self, slug: str) -> Optional[int]:
        """Get WordPress ID for a given slug"""
        return self.slug_to_id.get(slug)

