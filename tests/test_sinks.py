"""Behavioral tests for Fulfil's Airwallex wallet sinks."""

from __future__ import annotations

from types import SimpleNamespace

from target_fulfil.sinks import BankAccountsSink, BankStatementTransactionsSink


def make_sink(sink_class, state):
    """Build the minimum sink object needed by the public sink hooks."""
    sink = object.__new__(sink_class)
    sink.latest_state = state
    sink._target = SimpleNamespace(_latest_state=state)
    return sink


def test_bank_account_updates_the_record_saved_for_its_wallet():
    state = {
        "bookmarks": {"bank_accounts": [{"success": True, "externalId": "wallet-usd", "id": "42"}]}
    }
    sink = make_sink(BankAccountsSink, state)
    sent = {}
    sink.request_api = lambda method, endpoint, request_data: (
        sent.update(method=method, endpoint=endpoint, payload=request_data)
        or SimpleNamespace(json=lambda: {"id": "42"})
    )

    record_id, success, updates = sink.upsert_record(
        {
            "externalId": "wallet-usd",
            "wallet_external_id": "wallet-usd",
            "name": "Airwallex USD",
        },
        {},
    )

    assert (record_id, success, updates) == ("42", True, {"is_updated": True})
    assert sent == {
        "method": "PUT",
        "endpoint": "/model/bank/42",
        "payload": {"name": "Airwallex USD"},
    }


def test_bank_account_resolves_an_iso_currency_code():
    sink = make_sink(BankAccountsSink, {"bookmarks": {}})
    sink.currency_ids = {}
    sink.request_api = lambda *args, **kwargs: SimpleNamespace(json=lambda: [{"id": 99}])

    payload = sink.preprocess_record({"externalId": "wallet-usd", "currency": "USD"}, {})

    assert payload == {"currency": 99}


def test_transaction_resolves_its_bank_from_the_wallet_bookmark():
    state = {
        "bookmarks": {"bank_accounts": [{"success": True, "externalId": "wallet-usd", "id": "42"}]}
    }
    sink = make_sink(BankStatementTransactionsSink, state)

    payload = sink.preprocess_record(
        {"externalId": "txn-1", "bank_external_id": "wallet-usd", "amount": "12.50"}, {}
    )

    assert payload == {"amount": "12.50", "bank": "42"}
