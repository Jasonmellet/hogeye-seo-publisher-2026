"""
WordPress REST API Authentication Module
Handles authentication and connection testing
"""

from __future__ import annotations

import requests
from requests.auth import HTTPBasicAuth

from agt_publisher_core.config import Config


class WordPressAuth:
    """Handle WordPress REST API authentication"""

    def __init__(self):
        self.site_url = Config.WP_SITE_URL
        self.username = Config.WP_USERNAME
        self.app_password = Config.WP_APP_PASSWORD
        self.auth = HTTPBasicAuth(self.username, self.app_password)
        self.session = requests.Session()
        self.session.auth = self.auth
        # Add browser-like headers to avoid being blocked by security plugins
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
        )

    def test_connection(self):
        """
        Test connection to WordPress REST API
        Returns: (success: bool, message: str, data: dict)
        """
        try:
            # Test basic API access
            response = self.session.get(f"{self.site_url}/wp-json", timeout=10)

            if response.status_code != 200:
                return False, f"Failed to connect to WordPress API (Status: {response.status_code})", None

            site_info = response.json()

            # Test authenticated endpoint
            auth_response = self.session.get(Config.get_api_url("users/me"), timeout=10)

            if auth_response.status_code == 401:
                return False, "Authentication failed. Check your username and application password.", None

            if auth_response.status_code == 403:
                return False, "Authentication forbidden. User may not have required permissions.", None

            if auth_response.status_code != 200:
                return False, f"Authentication test failed (Status: {auth_response.status_code})", None

            user_info = auth_response.json()

            return True, "Successfully authenticated with WordPress!", {
                "site_name": site_info.get("name", "Unknown"),
                "site_description": site_info.get("description", ""),
                "wordpress_version": site_info.get("gmt_offset", "Unknown"),
                "user_name": user_info.get("name", "Unknown"),
                "user_id": user_info.get("id", "Unknown"),
                "user_roles": user_info.get("roles", []),
            }

        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to {self.site_url}. Check the URL.", None
        except requests.exceptions.Timeout:
            return False, "Connection timeout. WordPress site may be slow or unreachable.", None
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    def get_session(self):
        """Get authenticated requests session"""
        return self.session

    def check_permissions(self):
        """
        Check what permissions the authenticated user has
        Returns: dict with permission flags
        """
        permissions = {
            "can_publish_posts": False,
            "can_publish_pages": False,
            "can_upload_files": False,
            "can_manage_categories": False,
        }

        try:
            # Check if user can create posts (test with draft)
            test_post = {"title": "Permission Test (Do Not Publish)", "content": "Testing permissions", "status": "draft"}

            response = self.session.post(Config.get_api_url("posts"), json=test_post, timeout=10)

            if response.status_code in [200, 201]:
                permissions["can_publish_posts"] = True
                # Delete the test post
                post_id = response.json().get("id")
                if post_id:
                    self.session.delete(Config.get_api_url(f"posts/{post_id}"), params={"force": True})

            # Check if user can create pages
            test_page = {"title": "Permission Test (Do Not Publish)", "content": "Testing permissions", "status": "draft"}

            response = self.session.post(Config.get_api_url("pages"), json=test_page, timeout=10)

            if response.status_code in [200, 201]:
                permissions["can_publish_pages"] = True
                # Delete the test page
                page_id = response.json().get("id")
                if page_id:
                    self.session.delete(Config.get_api_url(f"pages/{page_id}"), params={"force": True})

            # Can upload files is usually tied to being able to post
            permissions["can_upload_files"] = permissions["can_publish_posts"]
            permissions["can_manage_categories"] = permissions["can_publish_posts"]

        except Exception as e:
            print(f"Warning: Could not fully check permissions: {e}")

        return permissions

