#!/usr/bin/env python3
"""
Preferred entry point for HogEye trap-release keyword analysis.

This script delegates to the existing implementation module for backward
compatibility with older automation.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    legacy_impl = Path(__file__).resolve().with_name("hogeye_ranch_camera_keyword_analysis.py")
    runpy.run_path(str(legacy_impl), run_name="__main__")

