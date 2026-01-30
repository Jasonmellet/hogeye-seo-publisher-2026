from __future__ import annotations

import json
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_CONFIG_PATH = REPO_ROOT / "work" / "seo" / "hogeye" / "PROJECT_CONFIG.json"


def _is_set(env_key: str) -> bool:
    v = os.getenv(env_key)
    return bool(v and v.strip())


def main() -> int:
    print("Hogeye preflight")
    print(f"- repo_root: {REPO_ROOT}")
    print(f"- config: {PROJECT_CONFIG_PATH}")

    if not PROJECT_CONFIG_PATH.exists():
        print("\nERROR: Missing PROJECT_CONFIG.json")
        print(f"Expected at: {PROJECT_CONFIG_PATH}")
        return 2

    try:
        cfg = json.loads(PROJECT_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print("\nERROR: Could not parse PROJECT_CONFIG.json")
        print(str(e))
        return 2

    client = cfg.get("client", {}) if isinstance(cfg, dict) else {}
    site_url = (client.get("site_url") if isinstance(client, dict) else "") or ""

    missing_cfg: list[str] = []
    if not str(site_url).strip():
        missing_cfg.append("client.site_url")

    print("\nConfig checks")
    if missing_cfg:
        for k in missing_cfg:
            print(f"- MISSING: {k}")
    else:
        print("- OK: required config present")

    required_env = [
        "WP_SITE_URL",
        "WP_USERNAME",
        "WP_APP_PASSWORD",
        "DATAFORSEO_LOGIN",
        "DATAFORSEO_PASSWORD",
        # Optional but common for planning:
        "SEO_SPREADSHEET_ID",
        "GOOGLE_APPLICATION_CREDENTIALS",
        # Optional for AI drafting:
        "ANTHROPIC_API_KEY",
    ]

    print("\nEnvironment checks (.env)")
    for k in required_env:
        status = "SET" if _is_set(k) else "missing"
        print(f"- {k}: {status}")

    print("\nNext")
    print("- Fill missing config/env values")
    print("- Then run the smoke tests in `work/seo/hogeye/RUNBOOK.md`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

