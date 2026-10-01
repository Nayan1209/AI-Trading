# Instrument Master Specification
**Version:** 0.1 | **Status:** Implemented in-memory registry; persistence pending

## Purpose
The instrument master is the canonical mapping between an internal instrument identity and exchange/broker identifiers. Strategy, scanner, market-data and future execution components must resolve instruments through this layer rather than hard-coding broker symbols or exchange tokens.

## Groww source fields
The first provider is Groww. Its instrument CSV supplies exchange, exchange token, trading symbol, Groww symbol, name, instrument type, segment, series, ISIN, underlying identifiers, expiry, strike, lot size, tick size, freeze quantity and trading permissions.

## Internal identity
```text
{EXCHANGE}:{SEGMENT}:{TRADING_SYMBOL}
```

Example:
```text
NSE:CASH:RELIANCE
```

## Required lookup paths
- Internal instrument ID
- Groww symbol
- Exchange + trading symbol
- Exchange + exchange token

## Normalization rules
- Exchange, segment, trading symbol and instrument type are normalized to uppercase.
- Exchange tokens are stored as strings to preserve provider identifiers safely.
- Monetary/price fields use `Decimal` rather than binary floating-point values.
- Empty optional provider fields become `None`.
- Provider permission flags are normalized to booleans.
- Duplicate canonical IDs, Groww symbols, exchange/symbol pairs or exchange/token pairs are rejected.

## India-first scope
The first production market is Indian equities. The master model supports derivative fields so the architecture does not need to be redesigned when F&O is introduced, but the initial stock universe should be explicitly filtered to the CASH segment.

## Safety boundary
This component only identifies instruments. It does not place orders, create positions, or grant trading permissions.

## Implementation
Current implementation:
- `src/market_data/instruments.py` — Pydantic instrument model, CSV normalization and in-memory lookup registry.
- `tests/test_instruments.py` — mapping, filtering, duplicate and validation tests.

## Future persistence
The PostgreSQL `instruments` table will become the durable source of truth after the instrument model and validation rules are stable. Database persistence is a separate milestone and must not be conflated with the current in-memory implementation.
