"""
Guardrails for WordPress REST DELETE operations.

By default the publisher stack does not call DELETE against WordPress. Scripts that
need rollback deletes must set WP_ALLOW_DELETE=true explicitly.
"""

from __future__ import annotations

from typing import Any

import requests

from agt_publisher_core.config import Config


class WordPressDeleteNotAllowed(RuntimeError):
    """Raised when code attempts a WP REST DELETE while WP_ALLOW_DELETE is not true."""


def wp_session_delete(session: requests.Session, url: str, **kwargs: Any) -> requests.Response:
    """
    Session.delete to WordPress — allowed only when Config.allow_wp_delete() is True.
    """
    if not Config.allow_wp_delete():
        raise WordPressDeleteNotAllowed(
            "WordPress DELETE is disabled by default. Set WP_ALLOW_DELETE=true in .env only if you "
            "explicitly accept permanent REST deletes (rollback scripts, cleanup tools)."
        )
    return session.delete(url, **kwargs)
