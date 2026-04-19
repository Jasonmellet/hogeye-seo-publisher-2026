#!/usr/bin/env python3
"""Deprecated alias — use hogeye_draft_md_to_post_json.py (same arguments)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_NEW = Path(__file__).resolve().parent / "hogeye_draft_md_to_post_json.py"


def main() -> int:
    return subprocess.call([sys.executable, str(_NEW)] + sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
