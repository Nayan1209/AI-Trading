# Scanner Feature Snapshot Specification
**Document ID:** DATA-013  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Deterministic descriptive features from the DATA-010 persisted LTP history boundary

## Objective

Provide the scanner with a deterministic, provider-independent snapshot of recent LTP history for the DATA-012 universe and market-data window. DATA-013 describes observed price data; it does not rank instruments, generate trading signals, call AI models, place orders, or execute trades.

## Feature Contract

`ScannerFeatureSnapshot` contains:

- canonical `internal_id`;
- trading symbol;
- number of valid LTP samples;
- first valid LTP in the bounded window;
- latest valid LTP in the bounded window;
- highest valid LTP;
- lowest valid LTP;
- percentage change from first to latest sample.

The percentage change is:

```text
(latest_ltp - first_ltp) / first_ltp × 100
```

All price values remain `Decimal` values. No floating-point conversion is introduced.

## Read Boundary

`ScannerFeatureService` reads only through the provider-independent LTP history contract equivalent to `PostgresLtpRepository.get_ltp()`.

The service receives a `ScannerUniverse` and `MarketDataWindow` from DATA-012. The repository range is half-open, so the service extends the upper bound by one microsecond to preserve DATA-012's inclusive reference-time semantics.

## Deterministic Eligibility

Only rows that satisfy all of the following contribute to a snapshot:

1. the returned `internal_id` matches the requested canonical ID;
2. the segment is `CASH`;
3. the timestamp is timezone-aware;
4. the timestamp is inside the DATA-012 inclusive window;
5. the LTP is positive.

Missing history produces no snapshot. Invalid rows are excluded rather than repaired or invented.

## Ordering

Snapshots are returned in the deterministic lexical order of `ScannerUniverse.internal_ids`. LTP history is expected in chronological order from the persistence boundary; the service uses the first and last valid rows as the bounded-window endpoints.

## Safety Boundary

DATA-013 is descriptive market-data preparation only. It introduces no signal score, strategy rule, AI decision, trade plan, risk override, broker connection, order placement, withdrawal capability, or live trading behavior.

## Acceptance Criteria

- Features are computed only from DATA-010 persisted LTP history.
- DATA-012 universe and window contracts remain authoritative.
- CASH-only and positive-LTP constraints remain enforced.
- Future and out-of-window rows are excluded.
- Empty history is handled deterministically.
- Percentage change uses `Decimal` arithmetic.
- The reference-time boundary remains inclusive.
- Tests require no Groww credentials or production PostgreSQL service.
- README and build-status documentation identify DATA-013 and its next CI gate.
