# PostgreSQL Market-Data Persistence Specification
**Document ID:** DATA-006  
**Status:** Implementation in progress  
**Scope:** Durable persistence and retrieval of validated historical market candles

## Objective

Persist the project's normalized `Candle` model in PostgreSQL without exposing database details to market-data providers or strategy components.

## Persistence Boundary

```text
Groww / Market Data Provider
          ↓
Internal Candle[]
          ↓
DATA-004 validation
          ↓
CandleRepository
          ↓
PostgreSQL candles
```

Only validated candles may cross into the persistence layer. The PostgreSQL adapter must never persist raw provider payloads.

## Schema

The first durable market-data table is `candles` with:

- `symbol`, `exchange`, `timeframe`
- timezone-aware `timestamp`
- fixed-precision `NUMERIC` OHLC prices
- `BIGINT` non-negative volume
- `created_at`
- unique identity on `(symbol, exchange, timeframe, timestamp)`
- lookup index on `(exchange, symbol, timeframe, timestamp)`

Timestamps are stored as PostgreSQL `TIMESTAMPTZ`. Monetary/price values use fixed-precision numeric storage rather than floating point.

## Write Semantics

`PostgresCandleRepository.upsert_candles()`:

1. validates every candle with the existing deterministic validator;
2. normalizes timestamps to UTC for storage;
3. inserts new candles;
4. updates OHLCV when the same candle identity/timestamp already exists;
5. commits one coherent batch.

This makes repeated historical ingestion idempotent for the same candle identity.

## Read Semantics

`get_candles()` requires timezone-aware range boundaries, rejects an invalid range, and returns candles in chronological order.

## Safety

- No Groww credential is required for repository unit tests.
- No live database is required by CI tests; database calls are exercised with deterministic fakes.
- No order or execution API is involved.
- Credentials remain outside GitHub.

## Acceptance Criteria

- PostgreSQL candle schema is versioned in a migration file.
- Validated candles can be upserted through a repository boundary.
- Duplicate candle identity is handled idempotently.
- Invalid candles are rejected before any database write.
- Candle ranges can be read back into the internal model.
- Timezone-aware timestamps and fixed-precision values are preserved.
- CI tests require no external PostgreSQL service or Groww credential.

## Next Gate

After DATA-006 CI is green, advance to deterministic **data-quality monitoring** for completeness, duplicates, gaps and persistence health before scanner/signal work begins.
