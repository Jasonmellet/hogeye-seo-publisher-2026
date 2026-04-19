"""Resolve the repo-relative client workspace directory (pipeline, PROJECT_CONFIG, etc.)."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def workspace_rel_parts() -> list[str]:
    """Segments under repo root. Default: single folder `workspace` (legacy env: HOGEYE_WORKSPACE_REL)."""
    raw = os.environ.get("WORKSPACE_REL", os.environ.get("HOGEYE_WORKSPACE_REL", "workspace")).strip()
    if not raw:
        return ["workspace"]
    return [p for p in raw.split("/") if p]


def workspace_rel_posix() -> str:
    """e.g. `workspace` or `clients/foo` for defaults in argparse help strings."""
    return "/".join(workspace_rel_parts())


def workspace_dir_under(project_root: Path) -> Path:
    """Workspace folder under an arbitrary project root (e.g. CLI --project-root)."""
    return project_root.joinpath(*workspace_rel_parts())


def workspace_root() -> Path:
    return workspace_dir_under(REPO_ROOT)
