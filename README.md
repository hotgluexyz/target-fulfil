# target-fulfil

Singer target for Fulfil bank feeds. It supports the two streams emitted by
the Airwallex ETL:

- `bank_accounts` creates one Fulfil bank account per mapped Airwallex wallet.
- `bank_statement_transactions` creates the wallet's settled transactions.

Transactions resolve their `bank` ID from the target state produced by the
`bank_accounts` stream. The source-stable `externalId` is stored in the target
state, never sent to Fulfil.

## Configuration

```json
{
  "access_key": "fulfil_pat_...",
  "base_url": "https://dev.fulfil.io/api/v2"
}
```

`base_url` is optional and defaults to the Fulfil dev environment. The token is
sent in the `X-API-KEY` header.

## Input contracts

`bank_accounts` must provide `externalId`, `wallet_external_id`, `name`,
`account`, `company`, `currency`, and `statement_import_start_date`.

`bank_statement_transactions` must provide `externalId`, `bank_external_id`,
`transaction_id`, `date`, `amount`, and optional `fees`, `description`, and
`reference`. Amounts follow Fulfil's convention: positive deposits and negative
withdrawals.

## Local verification

```bash
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/pytest
```
