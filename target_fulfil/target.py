"""Fulfil target class."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.target_sdk.target import TargetHotglue
from target_fulfil.sinks import BankAccountsSink, BankStatementTransactionsSink


class TargetFulfil(TargetHotglue):
    """Target for Fulfil."""

    name = "target-fulfil"
    SINK_TYPES = [BankAccountsSink, BankStatementTransactionsSink]

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_key",
            th.StringType(),
            required=True,
            description="Secret value sent as the API key (see access_key_header_name)",
        ),
        th.Property(
            "access_key_header_name",
            th.StringType,
            required=False,
            description="HTTP header name for the API key (default: x-api-key)",
        ),
        th.Property(
            "access_key_prefix",
            th.StringType,
            required=False,
            description="Optional prefix before the key value in the header (e.g. 'Bearer ')",
        ),
        th.Property(
            "base_url",
            th.StringType,
            required=False,
            description="Fulfil API root; defaults to the Fulfil dev environment.",
        ),
    ).to_dict()


if __name__ == "__main__":
    TargetFulfil.cli()
