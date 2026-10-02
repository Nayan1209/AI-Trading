# Scanner Universe & Deterministic Market-Data Window Specification
**Document ID:** DATA-012  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Deterministic scanner universe construction and bounded market-data windows on top of DATA-011

## Objective

Provide a stable scanner input boundary that determines **which canonical CASH instruments are read** and **which time window is considered current**. DATA-012 does not rank instruments, generate signals, call AI models, place orders, or execute trades.

## Scanner Universe Contract

`ScannerUniverse.from_internal_ids()` accepts canonical internal instrument IDs in the form:

```text
exchange:segment:symbol
```

The current India-first scanner universe is CASH-only.

The constructor:

- rejects an empty universe;
- rejects blank or malformed internal IDs;
- rejects non-CASH segments;
- rejects duplicate IDs;
- returns IDs in deterministic lexical order.

The resulting tuple is immutable and is the only instrument set passed to the scanner market-data consumer.

## Market-Data Window Contract

`MarketDataWindow` contains:

- `reference_time`: timezone-aware upper bound for the scan;
- `max_age`: non-negative freshness duration.

The inclusive read window is:

```text
start_time = reference_time - max_age
end_time   = reference_time
```

Both boundaries are deterministic and timezone-aware. Naive reference timestamps and negative freshness durations fail closed.

An event timestamp is considered inside the window only when it is timezone-aware and satisfies:

```text
start_time <= timestamp <= reference_time
```

Future timestamps are therefore outside the window.

## Scanner Integration

`ScannerUniverseService` composes the DATA-012 universe and window with `ScannerMarketDataService` from DATA-011.

```text
ScannerUniverse
      ↓
MarketDataWindow
      ↓
ScannerUniverseService
      ↓
ScannerMarketDataService
      ↓
ResolvedLtp → ScannerCandidate
```

The service continues to use only the DATA-010 controlled LTP read boundary. PostgreSQL rows and provider-specific Groww payloads remain outside the scanner contract.

## Determinism Rules

For the same universe and the same reference time/freshness window:

1. the same canonical IDs are requested;
2. IDs are requested in deterministic order;
3. the same inclusive time bounds are applied;
4. no missing data is invented;
5. no future data is accepted;
6. no signal or trading decision is produced.

## Acceptance Criteria

- CASH-only canonical universe is enforced.
- Duplicate and malformed instrument identities fail closed.
- Universe ordering is deterministic.
- Market-data window bounds are explicit and inclusive.
- Reference time must be timezone-aware.
- Freshness duration cannot be negative.
- Event timestamps must be timezone-aware when evaluated against the window.
- DATA-011 remains the only market-data eligibility/read consumer.
- Tests are deterministic and require no Groww credentials or production PostgreSQL service.
- README and build-status documentation identify DATA-012 and the next gate.

## Safety Boundary

DATA-012 introduces no signal generation, AI analysis, trade planning, risk bypass, broker execution, withdrawal capability, or live trading connection. It only organizes validated market-data inputs for the downstream scanner layer.
