# PAPER-007 — Deterministic Paper Portfolio Valuation Specification

## Objective

PAPER-007 adds a deterministic portfolio-level valuation boundary on top of completed PAPER-005 position accounting and PAPER-006 position valuation.

It accepts immutable `PaperPosition` snapshots plus an explicit current market price for every position and returns one immutable portfolio valuation snapshot.

## Scope

The boundary calculates:

- per-position mark-to-market valuation through PAPER-006
- aggregate market value
- aggregate realized P&L
- aggregate unrealized P&L
- aggregate total P&L
- deterministic position ordering by `position_key`

## Contract

The valuation engine must:

- accept only `PaperPosition` snapshots
- require exactly one positive `Decimal` market price for every position key
- reject duplicate position keys
- reject missing or unexpected market-price keys
- reject non-`Decimal` market prices
- reject non-positive market prices
- preserve immutable position valuation results
- return positions in deterministic sorted order
- return deterministic aggregate monetary values
- allow an empty portfolio and return zero aggregates

## Deterministic arithmetic

PAPER-006 remains the single position-level valuation authority. PAPER-007 delegates each position to that boundary and sums its monetary results.

Aggregate P&L values are normalized to `Decimal("0.01")` so portfolio totals remain deterministic and do not expose repeating-decimal artifacts.

## Safety boundary

PAPER-007 does not:

- call Groww
- access credentials or secrets
- use network transport
- mutate the position ledger
- persist to a database
- execute orders
- make trading decisions
- infer missing market prices

## Completion rule

PAPER-007 is complete only after implementation, deterministic tests, documentation, and automatic CI validation are green.
