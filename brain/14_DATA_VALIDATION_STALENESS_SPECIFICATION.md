# Data Validation & Staleness Specification
**Document ID:** DATA-004
**Status:** Implementation in progress
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

## Acceptance Criteria

- Valid candles pass all checks.
- Invalid OHLC relationships are rejected.
- Negative/non-positive prices are rejected.
- Negative volume is rejected.
- Naive timestamps are rejected.
- Future timestamps are rejected.
- Stale candles are detected using the supplied threshold.
- Fresh candles are accepted.
- Tests use deterministic fixture timestamps and do not call Groww.

## Next Gate

After CI passes, integrate this validation gate into `MarketDataService` before market data is exposed to scanner/signal components. Then update the build tracker and README before starting historical candle ingestion.
