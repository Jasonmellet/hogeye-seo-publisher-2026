"""
Compatibility wrapper.

New code should import:
  from agt_publisher_core.modules.acf_blocks import ...
"""

from agt_publisher_core.modules.acf_blocks import (  # re-export
    build_acf_page_content,
    create_clearfix_block,
    create_large_image_block,
    create_two_column_images_block,
    html_to_acf_content_block,
    split_content_by_h2,
)

