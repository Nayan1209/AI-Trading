# Real-Time LTP Feed Specification
**Document ID:** DATA-008  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Read-only normalization and deterministic freshness gating for Groww real-time LTP data

## Objective

Add the first controlled real-time market-data boundary after the historical/persistence/data-quality foundation. DATA-008 normalizes Groww LTP feed payloads into a provider-independent internal event model without enabling orders or requiring live credentials in CI.

## Provider Contract

Groww's Python SDK `GrowwFeed` can subscribe to live equity and derivative LTP data. Each event identifies the exchange, segment and exchange token and contains an epoch-millisecond timestamp plus the last traded price. The implementation keeps that provider-specific nesting at the adapter boundary.

## Internal Event

`LtpEvent` contains:

- `exchange`
- `segment`
- `exchange_token`
- timezone-aware UTC `timestamp`
- positive `Decimal` `ltp`

The event is immutable so downstream consumers cannot silently alter the normalized source event.

## Normalization

`normalize_groww_ltp()` converts one provider event into `LtpEvent`.

`normalize_groww_ltp_payload()` converts the complete nested Groww LTP mapping into a deterministic list of events. Malformed subscribed events are rejected rather than guessed.

## Freshness Gate

`validate_ltp_freshness()` fails closed when:

- the reference time is not timezone-aware;
- the configured maximum age is negative;
- the event timestamp is in the future; or
- the event is older than the caller-supplied freshness threshold.

The monitor does not invent exchange-session calendars.

## Safety Boundary

- DATA-008 is read-only.
- CI uses deterministic payload fixtures only.
- No Groww API key, access token or TOTP is required for tests.
- No websocket/network connection is opened by the normalization module.
- No order, withdrawal or execution functionality is involved.
- Malformed or stale market data is rejected instead of guessed.

## Acceptance Criteria

- Groww LTP payloads normalize into a provider-independent event model.
- Epoch-millisecond timestamps become timezone-aware UTC datetimes.
- LTP values are represented as `Decimal` and must be greater than zero.
- Exchange, segment and exchange token identity is preserved.
- Nested multi-instrument payloads are supported.
- Stale and future events fail the deterministic freshness gate.
- Malformed events fail closed.
- Unit tests use no live Groww service or credential.
- README and build-status documentation are updated.

## Next Gate

After DATA-008 automatic CI is green, integrate the normalized LTP stream with the existing instrument registry, data-quality boundary and persistence path before scanner/signal work. Live Groww connectivity remains an operational step and must not be enabled implicitly by unit-test code.
