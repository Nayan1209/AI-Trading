# Historical Candle Ingestion Specification
**Document ID:** DATA-005  
**Status:** Implementation in progress  
**Scope:** Read-only historical OHLCV ingestion through the market-data provider boundary

## Objective

Provide deterministic historical candle ingestion without exposing Groww SDK types to the rest of the application.

## Provider Contract

The market-data provider exposes historical candles as the project's internal `Candle` model:

```text
Provider API
    ↓
Raw historical response
    ↓
Timestamp / numeric normalization
    ↓
Internal Candle[]
    ↓
MarketDataService validation gate
```

The provider request uses an instrument's Groww symbol, exchange, timezone-aware start/end timestamps, and an interval expressed in minutes.

## Groww Mapping

Groww's current Python SDK uses `get_historical_candles()` with `exchange`, `segment`, `groww_symbol`, `start_time`, `end_time`, and `candle_interval`. The response contains candle rows with timestamp, OHLC, volume and, for FNO, optional open interest. The first implementation stores the common OHLCV fields in `Candle`; open interest is intentionally deferred until the derivative data model requires it.

Groww's current documentation provides different request-duration/history limits by candle interval. The ingestion layer therefore accepts an explicit interval and does not silently expand a requested range.

## Timestamp Rules

- Caller timestamps must be timezone-aware.
- Requests are formatted for Groww in India Standard Time.
- Groww historical timestamps without an explicit timezone are interpreted as `Asia/Kolkata`.
- Epoch timestamps are interpreted according to the documented historical-candle response format and normalized to timezone-aware datetimes.

## Validation Boundary

`MarketDataService.historical()` validates every returned candle with the existing deterministic DATA-004 validator before exposing the list downstream.

A malformed candle fails closed. No AI or strategy component is allowed to consume an unvalidated historical candle.

## Safety

- Historical ingestion is read-only.
- No order API is called.
- Tests use a fake Groww client and deterministic fixtures.
- No Groww access token or API secret is stored in the repository.

## Acceptance Criteria

- Groww historical response rows normalize into internal `Candle` objects.
- Seven-field rows containing optional open interest are accepted without leaking OI into the current model.
- Returned timestamps are timezone-aware.
- Invalid request ranges are rejected before the provider call.
- `MarketDataService.historical()` validates every candle.
- No live Groww credential is required by CI tests.

## Next Gate

After DATA-005 CI is green, the next milestone is PostgreSQL persistence for validated historical market data. Persistence must consume validated candles rather than raw provider responses.
