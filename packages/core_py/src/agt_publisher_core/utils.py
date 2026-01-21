from __future__ import annotations

from pathlib import Path
from typing import Optional


def find_upwards(filename: str, *, start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find a file by walking upward from start_dir (or cwd) to filesystem root.
    Returns the first match, or None.
    """
    cur = (start_dir or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        cand = p / filename
        if cand.exists():
            return cand
    return None

