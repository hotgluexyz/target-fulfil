"""HTTP client and sink base classes for Fulfil."""

from __future__ import annotations

import json
from typing import Any, ClassVar

from hotglue_singer_sdk.target_sdk.auth import ApiAuthenticator
from hotglue_singer_sdk.target_sdk.client import HotglueBaseSink, HotglueSink


class FulfilSink(HotglueBaseSink):
    """Fulfil Base target sink class for sinks."""

    default_base_url = "https://dev.fulfil.io/api/v2"
    auth_state: ClassVar[dict] = {}
    currency_ids: ClassVar[dict[str, int]] = {}
    created_bank_ids: ClassVar[dict[str, str]] = {}

    @property
    def base_url(self) -> str:
        return self.config.get("base_url", self.default_base_url).rstrip("/")

    @property
    def authenticator(self) -> Any:
        return ApiAuthenticator(
            self._target,
            self.auth_state,
            header_name=self.config.get("access_key_header_name", "x-api-key"),
            header_value_prefix=self.config.get("access_key_prefix", ""),
            config_key="access_key",
        )

    def resolve_currency(self, currency: str | int) -> str | int:
        """Resolve an ISO code to the Fulfil currency record ID."""
        if isinstance(currency, int) or currency.isdigit():
            return currency
        if currency not in self.currency_ids:
            response = self.request_api(
                "GET",
                "/model/currency",
                params={"filter": json.dumps([["code", "=", currency]])},
            )
            matches = response.json()
            if len(matches) != 1:
                raise ValueError(f"Fulfil currency '{currency}' was not found")
            self.currency_ids[currency] = matches[0]["id"]
        return self.currency_ids[currency]


class FulfilRecordSink(FulfilSink, HotglueSink):
    """Fulfil Record target sink class for record sinks."""

    name = "FulfilRecordSink"

    def preprocess_record(self, record: dict, context: dict) -> dict:
        return record

    def state_id_for_external_id(self, stream: str, external_id: str) -> str | None:
        """Return the Fulfil ID previously emitted for a stable source ID."""
        state = self.latest_state or self._target._latest_state or {}
        for bookmark in state.get("bookmarks", {}).get(stream, []):
            if bookmark.get("success") and bookmark.get("externalId") == external_id:
                return bookmark.get("id")
        return None
