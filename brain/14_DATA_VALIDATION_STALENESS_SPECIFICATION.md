# Data Validation & Staleness Specification
**Document ID:** DATA-004
**Status:** CI validation pending
**Scope:** Deterministic market-data quality gates before scanner/signal consumption

## Objective

Prevent malformed, contradictory, or stale market data from entering downstream strategy and AI components.

## Validation Rules

Every normalized `Candle` must satisfy:

1. `symbol`, `exchange`, and `timeframe` are non-empty.
2. `timestamp` must be timezone-aware.
3. `open`, `high`, `low`, and `close` must be strictly greater than zero.
4. `high >= max(open, close)`.
5. `low <= min(open, close)`.
6. `high >= low`.
7. `volume >= 0`.

A candle failing any deterministic rule is rejected and must not reach the signal engine.

## Staleness

Staleness is evaluated against an explicit caller-supplied `max_age` rather than a hard-coded provider assumption.

```text
age = reference_time - candle.timestamp
stale = age > max_age
```

Both timestamps must be timezone-aware. A candle timestamp in the future relative to the reference time is rejected as invalid rather than silently treated as fresh.

## Design Rules

- Validation is deterministic and independent of the AI model.
- The validator does not mutate market data.
- Provider-specific timestamp and interval semantics must be normalized before validation.
- Provider outages or stale feeds must fail closed for downstream trading decisions.
- No live Groww credential is required for validation tests.

## Service Integration

`MarketDataService.latest()` now applies `validate_candle()` immediately after provider retrieval and rejects stale candles using the supplied `max_age` threshold. A caller may provide `reference_time` for deterministic tests; production callers default to the current UTC time.

The service therefore exposes a candle downstream only after both deterministic validation and freshness checks pass.

## Acceptance Criteria

- Valid candles pass all checks.
- Invalid OHLC relationships are rejected.
- Negative/non-positive prices are rejected.
- Negative volume is rejected.
- Naive timestamps are rejected.
- Future timestamps are rejected.
- Stale candles are detected using the supplied threshold.
- Fresh candles are accepted.
- `MarketDataService` rejects malformed or stale provider output before returning it.
- Tests use deterministic fixture timestamps and do not call Groww.

## Next Gate

Run the DATA-004 CI gate only after the complete implementation and documentation change set has passed preflight review. If CI passes, mark DATA-004 complete and proceed to historical candle ingestion. If CI fails, fix the failing test/build before adding new functionality.
