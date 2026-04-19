"""
Repo path bootstrap for `scripts/publisher/` CLIs and legacy `modules` imports.

Entry scripts call `_publisher_bootstrap()` (inline) which loads this module
via importlib and invokes `ensure_publisher_paths()`.
"""
from __future__ import annotations

import sys
from pathlib import Path


def ensure_publisher_paths() -> Path:
    """Add repo root, scripts/publisher, and packages/core_py/src to sys.path."""
    root = Path(__file__).resolve().parents[2]
    marker = root / "packages" / "core_py" / "src"
    if not marker.is_dir():
        raise RuntimeError("publisher site_setup: could not locate repo root (packages/core_py/src not found)")
    rs = str(root)
    sp = str(root / "scripts" / "publisher")
    src = str(marker)
    for p in (rs, sp, src):
        if p not in sys.path:
            sys.path.insert(0, p)
    return root
