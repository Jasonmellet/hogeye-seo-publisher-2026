from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agt_publisher_core.client_config import ClientConfig, compare_wp_host, compare_wp_target
from agt_publisher_core.config import Config


@dataclass(frozen=True)
class PreflightInfo:
    client_name: str
    expected_wp_site_url: str
    actual_wp_site_url: str
    detected_site_name: Optional[str]


def run_publish_preflight(
    *,
    client: ClientConfig,
    detected_site_name: Optional[str],
    status: str,
    assume_yes: bool,
) -> PreflightInfo:
    """
    Hard guardrails to prevent wrong-site publishing.

    - Requires committed `client.config.json`.
    - Verifies `.env` target matches expected URL + host.
    - If publishing to `publish`, requires explicit human confirmation unless `--yes`.
    """
    Config.validate()

    ok, msg = compare_wp_target(expected_site_url=client.expectedWpSiteUrl, actual_site_url=Config.WP_SITE_URL)
    if not ok:
        raise ValueError(msg)

    ok, msg = compare_wp_host(expected_host=client.expectedWpSiteHost, actual_site_url=Config.WP_SITE_URL)
    if not ok:
        raise ValueError(msg)

    if client.expectedWpSiteName and detected_site_name:
        # soft check: name mismatch forces confirmation on publish
        name_match = client.expectedWpSiteName.strip().lower() == detected_site_name.strip().lower()
    else:
        name_match = True

    if status == "publish" and not assume_yes:
        expected = client.clientName.strip()
        prompt = (
            "\nSAFETY CHECK\n"
            f"- clientName: {client.clientName}\n"
            f"- WP_SITE_URL: {Config.WP_SITE_URL}\n"
            f"- detectedSiteName: {detected_site_name or '(unknown)'}\n"
            "\nTo continue, type the clientName exactly and press Enter: "
        )
        typed = input(prompt).strip()
        if typed != expected:
            raise ValueError("Publish cancelled: confirmation did not match clientName.")

    if status == "publish" and not name_match and assume_yes:
        # In automation we still want to block obvious mismatch, because `--yes` is easy to misuse.
        raise ValueError(
            f"Publish blocked: detected site name '{detected_site_name}' does not match expectedWpSiteName '{client.expectedWpSiteName}'."
        )

    return PreflightInfo(
        client_name=client.clientName,
        expected_wp_site_url=client.expectedWpSiteUrl.rstrip("/"),
        actual_wp_site_url=Config.WP_SITE_URL.rstrip("/"),
        detected_site_name=detected_site_name,
    )

