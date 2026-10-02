# Scanner-Ready Market-Data Consumer Specification
**Document ID:** DATA-011  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Deterministic scanner input selection from the DATA-010 controlled LTP read boundary

## Objective

Provide the first scanner-ready market-data consumer without introducing signal generation, AI decisions, orders, withdrawals or live execution.

## Read Flow

```text
PostgreSQL ltp_events
        ↓
PostgresLtpRepository.get_latest_ltp()
        ↓
ResolvedLtp
        ↓
ScannerMarketDataService
        ↓
ScannerCandidate
```

## Scanner Input Contract

`ScannerMarketDataService` accepts canonical `internal_id` values and reads only through the DATA-010 `get_latest_ltp()` contract.

The scanner never queries PostgreSQL directly and never consumes raw Groww payloads, provider tokens or database rows.

Each eligible result is a provider-independent `ScannerCandidate` containing:

- canonical `internal_id`
- trading symbol
- exchange
- segment
- UTC-capable event timestamp
- positive `Decimal` LTP

## Deterministic Eligibility Rules

An instrument is eligible only when all of the following are true:

1. A latest persisted LTP exists.
2. The returned `internal_id` matches the requested canonical ID.
3. The instrument segment is `CASH` for the current India-first scanner scope.
4. The LTP is greater than zero.
5. The event timestamp is timezone-aware.
6. The event timestamp is not in the future relative to the supplied reference time.
7. The event age does not exceed the caller-supplied `max_age`.

Missing or stale data is excluded. Future-dated data is excluded. No market data is invented.

## Safety Boundary

DATA-011 does not rank instruments, generate signals, call an AI model, place orders, connect to a live broker, or bypass the risk engine.

The scanner is a consumer of validated and persisted market data only.

## Acceptance Criteria

- Scanner reads only through the DATA-010 LTP read contract.
- Eligibility is deterministic and provider-independent.
- CASH is the only scanner-ready segment in the current India-first scope.
- Missing, stale and future-dated data is excluded.
- Invalid reference-time and freshness inputs fail closed.
- Read-boundary identity mismatches fail closed.
- Tests use deterministic in-memory fixtures with no Groww credentials or PostgreSQL service.
- README and build-status documentation identify DATA-011 as complete and the next gate clearly.
