# PAPER-005 — Deterministic Paper Position Accounting

## Purpose

PAPER-005 adds a deterministic in-process position-accounting boundary on top of completed paper fills.

It converts immutable `PaperOrder` fills into immutable position snapshots and realized P&L without broker access, database persistence, market-price lookups, or live execution.

## Inputs

- Immutable `PaperOrder`
- Explicit caller-supplied `position_key`

The current `PaperOrder` contract intentionally does not carry instrument identity. Therefore the position key is supplied explicitly at this boundary rather than inferred or invented.

## Rules

1. Only `PaperOrder` instances with status `FILLED` are accepted.
2. `position_key` must be a non-empty string.
3. BUY orders increase a long position and use weighted-average entry pricing.
4. SELL orders reduce an existing long position.
5. A SELL may not exceed the current long quantity.
6. Opening or maintaining short positions is not supported by PAPER-005.
7. The same `order_id` cannot be applied twice.
8. Realized P&L for a SELL is `(sell_price - average_entry_price) * quantity_sold`.
9. A position reaching zero quantity is retained as a zero-quantity snapshot with its accumulated realized P&L.
10. Snapshots are immutable and deterministic.

## Explicit non-goals

PAPER-005 does not implement:

- broker connectivity
- live order submission
- database persistence
- exchange matching
- slippage
- fees/taxes
- partial fills
- mark-to-market valuation
- unrealized P&L
- short selling
- portfolio risk approval
- credential access

## Safety

PAPER-005 is simulation-only. It has no network dependency and cannot place a real order.

## Completion rule

PAPER-005 is complete only after implementation, deterministic tests, documentation, and automatic CI validation are green.
