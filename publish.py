#!/usr/bin/env python3
"""
DEPRECATED ENTRYPOINT

This repo now uses the canonical pipeline scripts:
- publish_content_item.py
- publish_batch.py

This file exists only to prevent confusion from older docs/notes.
"""

from modules.deprecation import deprecated_script_exit


def main() -> None:
    deprecated_script_exit(
        script_name="publish.py",
        replacement="python publish_content_item.py /abs/path/to/content/posts/my-post.json --type posts\n"
        "or: python publish_batch.py /abs/path/to/content/posts --type posts",
    )


if __name__ == "__main__":
    main()

