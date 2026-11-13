"""Basic configuration tests for target-fulfil."""

from __future__ import annotations

from target_fulfil.target import TargetFulfil


def test_target_requires_an_api_key() -> None:
    """Expose the configured Fulfil API key field to Singer clients."""
    properties = TargetFulfil.config_jsonschema["properties"]

    assert "access_key" in properties
    assert "access_key" in TargetFulfil.config_jsonschema["required"]


def test_base_url_defaults_to_workspace_root() -> None:
    """Advertise the workspace URL rather than the versioned API URL."""
    assert (
        TargetFulfil.config_jsonschema["properties"]["base_url"]["default"]
        == "https://dev.fulfil.io"
    )
