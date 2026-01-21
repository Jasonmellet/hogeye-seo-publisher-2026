"""
Configuration loader for the publisher.

Design goals:
- Loads `.env` from the client repo root (current working directory) by default.
- Keeps configuration minimal and explicit for safety across many client repos.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    # Prefer repo-root .env when running commands from the client repo.
    env_path = Path(os.getenv("ENV_PATH") or (Path.cwd() / ".env"))
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


_load_env()


class Config:
    """Configuration class for WordPress publisher"""

    # WordPress credentials
    WP_SITE_URL = os.getenv("WP_SITE_URL", "").rstrip("/")
    WP_USERNAME = os.getenv("WP_USERNAME", "")
    WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

    # Optional settings
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Paths (relative to repo root; default is cwd)
    BASE_DIR = Path(os.getenv("PROJECT_ROOT", str(Path.cwd()))).resolve()
    CONTENT_DIR = BASE_DIR / "content"
    PAGES_DIR = CONTENT_DIR / "pages"
    POSTS_DIR = CONTENT_DIR / "posts"
    IMAGES_DIR = CONTENT_DIR / "images"
    LOGS_DIR = BASE_DIR / "logs"

    @classmethod
    def validate(cls) -> bool:
        errors = []
        if not cls.WP_SITE_URL:
            errors.append("WP_SITE_URL is not set in .env file")
        if not cls.WP_USERNAME:
            errors.append("WP_USERNAME is not set in .env file")
        if not cls.WP_APP_PASSWORD:
            errors.append("WP_APP_PASSWORD is not set in .env file")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        return True

    @classmethod
    def is_dry_run(cls) -> bool:
        return cls.DRY_RUN

    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        return f"{cls.WP_SITE_URL}/wp-json/wp/v2/{endpoint}"

    @classmethod
    def ensure_directories(cls) -> None:
        cls.PAGES_DIR.mkdir(parents=True, exist_ok=True)
        cls.POSTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

