"""
Compatibility wrapper.

New code should import:
  from agt_publisher_core.modules.transforms import ...
"""

from agt_publisher_core.modules.transforms import (  # re-export
    H2_STYLE,
    H3_STYLE,
    LI_STYLE,
    P_STYLE,
    add_spacing_to_html,
    ensure_unique_heading_ids,
    fix_malformed_h2_styles,
    insert_toc_after_intro,
    normalize_whitespace,
    remove_all_tocs,
)

