"""
Compatibility wrapper.

New code should import:
  from agt_publisher_core.modules.validators import ...
"""

from agt_publisher_core.modules.validators import (  # re-export
    ValidationResult,
    validate_blog_post,
    validate_landing_page,
)

