#!/usr/bin/env python3
"""
DEPRECATED ENTRYPOINT

This repo now uses the canonical pipeline scripts under scripts/publisher/:
- publish_content_item.py
- publish_batch.py

This file exists only to prevent confusion from older docs/notes.
"""

def _publisher_bootstrap() -> None:
    import importlib.util
    from pathlib import Path
    p = Path(__file__).resolve()
    for c in p.parents:
        su = c / "scripts" / "publisher" / "site_setup.py"
        if su.is_file():
            spec = importlib.util.spec_from_file_location("_publisher_site_setup", su)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.ensure_publisher_paths()
            return
    raise RuntimeError("Could not find scripts/publisher/site_setup.py")

_publisher_bootstrap()

from modules.deprecation import deprecated_script_exit


def main() -> None:
    deprecated_script_exit(
        script_name="publish.py",
        replacement="python scripts/publisher/publish_content_item.py /abs/path/to/content/posts/my-post.json --type posts\n"
        "or: python scripts/publisher/publish_batch.py /abs/path/to/content/posts --type posts",
    )


if __name__ == "__main__":
    main()
