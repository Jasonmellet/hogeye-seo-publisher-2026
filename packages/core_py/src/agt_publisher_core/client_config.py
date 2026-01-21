from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

try:
    from importlib import resources as importlib_resources  # py3.9+
except Exception:  # pragma: no cover
    import importlib_resources  # type: ignore


@dataclass(frozen=True)
class ClientConfig:
    schemaVersion: int
    clientName: str
    expectedWpSiteUrl: str
    expectedWpSiteHost: str
    expectedWpSiteName: Optional[str]
    environment: str
    linkAliases: Optional[Dict[str, str]]
    protectedMarkersBySlug: Optional[Dict[str, list[str]]]

    @property
    def expected_wp_origin(self) -> str:
        return self.expectedWpSiteUrl.rstrip("/")


def _load_schema() -> Dict[str, Any]:
    with importlib_resources.files("agt_publisher_core.schemas").joinpath("client_config.schema.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate(raw: Dict[str, Any]) -> Tuple[bool, list[str]]:
    schema = _load_schema()
    v = Draft202012Validator(schema)
    errors = []
    for e in sorted(v.iter_errors(raw), key=lambda x: x.path):
        loc = ".".join([str(p) for p in e.path]) if e.path else "(root)"
        errors.append(f"{loc}: {e.message}")
    return len(errors) == 0, errors


def load_client_config(repo_root: Optional[str] = None) -> ClientConfig:
    """
    Load and validate client config. Intended to be committed per-client.

    Default location: <repo_root>/client.config.json, where repo_root defaults to cwd.
    """
    root = Path(repo_root or Path.cwd()).resolve()
    path = root / "client.config.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing client config: {path}. Create it from client.config.example.json.")

    raw = json.loads(path.read_text(encoding="utf-8"))
    ok, errs = _validate(raw)
    if not ok:
        raise ValueError("client.config.json failed schema validation:\n  - " + "\n  - ".join(errs))

    # Light sanity check: host matches URL host when both provided.
    exp_url = str(raw.get("expectedWpSiteUrl") or "").rstrip("/")
    exp_host = str(raw.get("expectedWpSiteHost") or "").lower()
    parsed = urlparse(exp_url)
    if parsed.hostname and exp_host and parsed.hostname.lower() != exp_host:
        raise ValueError(
            "client.config.json mismatch: expectedWpSiteHost does not match expectedWpSiteUrl host.\n"
            f"  expectedWpSiteUrl host: {parsed.hostname.lower()}\n"
            f"  expectedWpSiteHost: {exp_host}"
        )

    return ClientConfig(
        schemaVersion=int(raw["schemaVersion"]),
        clientName=str(raw["clientName"]),
        expectedWpSiteUrl=exp_url,
        expectedWpSiteHost=exp_host,
        expectedWpSiteName=(str(raw["expectedWpSiteName"]) if raw.get("expectedWpSiteName") else None),
        environment=str(raw["environment"]),
        linkAliases=(dict(raw["linkAliases"]) if isinstance(raw.get("linkAliases"), dict) else None),
        protectedMarkersBySlug=(dict(raw["protectedMarkersBySlug"]) if isinstance(raw.get("protectedMarkersBySlug"), dict) else None),
    )


def compare_wp_target(*, expected_site_url: str, actual_site_url: str) -> Tuple[bool, str]:
    exp = expected_site_url.rstrip("/")
    act = actual_site_url.rstrip("/")
    if exp == act:
        return True, "ok"
    return False, f"WP_SITE_URL mismatch: expected {exp} but got {act}"


def compare_wp_host(*, expected_host: str, actual_site_url: str) -> Tuple[bool, str]:
    act_host = (urlparse(actual_site_url).hostname or "").lower()
    exp_host = (expected_host or "").lower()
    if act_host == exp_host:
        return True, "ok"
    return False, f"WP host mismatch: expected {exp_host} but got {act_host or '(none)'}"

