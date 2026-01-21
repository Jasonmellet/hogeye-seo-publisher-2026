"""
Deprecation guard for legacy one-off scripts.

We keep older scripts for reference, but we don't want them used in the monthly workflow,
because they can reintroduce duplication/drift.
"""

from __future__ import annotations

import os


def deprecated_script_exit(script_name: str, replacement: str) -> None:
    """
    Exit unless ALLOW_DEPRECATED_SCRIPTS=1 is set.
    """
    if os.environ.get("ALLOW_DEPRECATED_SCRIPTS") == "1":
        return
    raise SystemExit(
        f"{script_name} is DEPRECATED.\n"
        f"Use: {replacement}\n"
        f"If you truly need to run this legacy script, set ALLOW_DEPRECATED_SCRIPTS=1."
    )

