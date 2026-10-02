# Real-Time LTP Integration Specification
**Document ID:** DATA-009  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Resolve normalized Groww LTP events through the instrument registry and persist validated events

## Objective

Connect the DATA-008 normalized real-time LTP boundary to the existing instrument identity and persistence layers without enabling orders or requiring live Groww credentials in CI.

## Integration Flow

```text
Groww LTP payload
      ↓
DATA-008 normalization
      ↓
Freshness / fail-closed validation
      ↓
InstrumentMaster exchange-token lookup
      ↓
Canonical internal instrument identity
      ↓
PostgreSQL LTP persistence
```

## Instrument Resolution

`RealtimeLtpService` resolves every event using the canonical `(exchange, exchange_token)` mapping already maintained by `InstrumentMaster`.

Unknown exchange/token pairs are rejected. A segment mismatch between the provider event and canonical instrument is also rejected. The service never guesses an instrument from a symbol or nearest match.

## Persistence

`PostgresLtpRepository` stores only normalized, instrument-resolved events in the `ltp_events` table.

The persistence identity is `(internal_id, timestamp)`, allowing repeated delivery of the same event to be handled idempotently. Exchange, segment, exchange token and LTP are retained for reconciliation and downstream market-data consumers.

The migration is versioned under `database/migrations/002_ltp_events.sql`.

## Quality Boundary

The service reuses DATA-008's deterministic freshness gate. It fails closed when an event is stale or future-dated. Normalization failures, unknown instruments and segment mismatches are also rejected before persistence.

The existing candle data-quality monitor remains candle-specific; this milestone does not invent candle-style completeness rules for a tick/LTP stream.

## Safety Boundary

- DATA-009 remains read-only.
- No live Groww connection is opened by CI.
- No Groww API key, access token or TOTP is required by tests.
- No order, withdrawal or execution functionality is involved.
- Provider payloads are normalized before persistence.
- Unknown or invalid market data is rejected rather than guessed.

## Acceptance Criteria

- Normalized LTP events resolve through the canonical instrument registry.
- Unknown exchange/token mappings fail closed.
- Segment mismatches fail closed.
- Freshness validation runs before persistence.
- Valid resolved LTP events are persisted through a provider-independent repository boundary.
- PostgreSQL persistence is idempotent on internal instrument identity and event timestamp.
- Deterministic tests cover resolution, rejection and persistence behavior.
- README and build-status documentation are updated.

## Next Gate

After DATA-009 automatic CI is green, the next market-data milestone is to expose a controlled read path for the persisted real-time stream to scanner-ready consumers. Scanner/signal generation must remain downstream of the validated market-data boundary.
