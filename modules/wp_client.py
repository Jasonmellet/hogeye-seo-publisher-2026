"""
Compatibility wrapper.

New code should import:
  from agt_publisher_core.modules.wp_client import WordPressClient
"""

from agt_publisher_core.modules.wp_client import WPResponse, WordPressClient, clean_json_response  # re-export

