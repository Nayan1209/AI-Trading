# PAPER-006 — Deterministic Paper Position Valuation Specification

## Objective

PAPER-006 adds a deterministic mark-to-market valuation boundary on top of the completed PAPER-005 long-only position ledger. It calculates current market value, unrealized P&L, and total P&L from an immutable `PaperPosition` snapshot and a caller-supplied positive market price.

## Contract

The valuation boundary:

- accepts only a `PaperPosition` snapshot
- requires a positive current market price
- supports the existing long-only position semantics
- calculates market value as `quantity × current_price`
- calculates unrealized P&L as `(current_price − average_entry_price) × quantity`
- exposes realized P&L unchanged from PAPER-005
- calculates total P&L as `realized_pnl + unrealized_pnl`
- uses an explicit deterministic Decimal precision contract
- returns an immutable valuation snapshot
- does not mutate the PAPER-005 position ledger
- does not require broker/network access
- does not access credentials or secrets

## Empty Position

A zero-quantity position is valid. Its market value and unrealized P&L are zero regardless of the supplied positive market price. The stored realized P&L remains unchanged.

## Rejection Rules

Reject:

- non-`PaperPosition` inputs
- non-`Decimal` current prices
- zero or negative current prices

## Safety Boundary

PAPER-006 is valuation only. It does not execute orders, alter positions, submit broker requests, persist data, or make trading decisions.

## Completion Rule

PAPER-006 is complete only after implementation, deterministic tests, documentation, and automatic CI validation are green.
