"""Fulfil sinks for Airwallex wallet accounts and transactions."""

from __future__ import annotations

from decimal import Decimal

from target_fulfil.client import FulfilRecordSink


class BankAccountsSink(FulfilRecordSink):
    """Create a Fulfil bank account for each mapped Airwallex wallet."""

    name = "bank_accounts"
    endpoint = "/model/bank"

    def preprocess_record(self, record: dict, context: dict) -> dict:
        record = dict(record)
        record.pop("externalId", None)
        record.pop("external_id", None)
        record.pop("metadata", None)
        record.setdefault("type", "bank")
        record["currency"] = self.resolve_currency(record["currency"])
        return record

    def upsert_record(self, record: dict, context: dict):
        record.pop("externalId", None)
        record.pop("external_id", None)
        external_id = record.pop("wallet_external_id")
        existing_id = self.state_id_for_external_id(self.name, external_id)
        if existing_id:
            response = self.request_api(
                "PUT", f"{self.endpoint}/{existing_id}", request_data=record
            )
            record_id = response.json().get("id", existing_id)
            updates = {"is_updated": True}
        else:
            response = self.request_api("POST", self.endpoint, request_data=[record])
            record_id = response.json()[0]["id"]
            updates = {}

        self.created_bank_ids[external_id] = str(record_id)
        return record_id, True, updates


class BankStatementTransactionsSink(FulfilRecordSink):
    """Create each settled Airwallex transaction in its Fulfil bank feed."""

    name = "bank_statement_transactions"
    endpoint = "/model/bank_statement_transaction"

    def preprocess_record(self, record: dict, context: dict) -> dict:
        record = dict(record)
        record.pop("externalId", None)
        record.pop("external_id", None)
        record.pop("metadata", None)
        bank_external_id = record.pop("bank_external_id")
        bank_id = self.state_id_for_external_id(
            "bank_accounts", bank_external_id
        ) or self.created_bank_ids.get(bank_external_id)
        if not bank_id:
            raise ValueError(
                f"Airwallex wallet '{bank_external_id}' has not been created in Fulfil. "
                "Emit bank_accounts before bank_statement_transactions."
            )
        record["bank"] = bank_id
        record["amount"] = f"{Decimal(str(record['amount'])):.2f}"
        record["fees"] = f"{Decimal(str(record.get('fees', 0))):.2f}"
        return record

    def upsert_record(self, record: dict, context: dict):
        record.pop("externalId", None)
        record.pop("external_id", None)
        response = self.request_api("POST", self.endpoint, request_data=[record])
        return response.json()[0]["id"], True, {}
