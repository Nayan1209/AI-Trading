# RISK-002 Portfolio Exposure & Concentration Specification

**Document ID:** RISK-002  
**Status:** Implementation started  
**Parent:** Phase 5 — Trade Planner & Risk Engine  
**Depends on:** RISK-001, PLAN-001

## Objective

Add a deterministic portfolio-level safety gate before any future execution boundary. RISK-002 evaluates the proposed trade against current open-position exposure, single-symbol concentration, and maximum open-position count.

## Required behavior

- Accept explicit account equity and configured portfolio limits.
- Measure current and projected **gross notional exposure**; do not silently net positions or infer leverage.
- Measure projected concentration for the candidate symbol.
- Count distinct open symbols and include the candidate only when it is a new symbol.
- Reject any portfolio state or candidate that violates an explicit limit.
- Reject missing, malformed, non-positive, or ambiguous position inputs rather than guessing.
- Produce a deterministic immutable result for an approved candidate.
- Never access broker state, credentials, network services, or model providers.
- Never place, modify, or cancel orders.

## Conservative exposure semantics

RISK-002 uses gross notional exposure. Existing position notional and proposed trade notional are added even when their directions could theoretically offset. This avoids assuming that an execution system will net, reduce, or reconcile positions correctly.

A candidate for an already-open symbol increases that symbol's projected exposure but does not increase the distinct open-position count. A candidate for a new symbol increases the count by one.

## Acceptance criteria

1. A candidate inside all configured limits is approved.
2. Portfolio exposure above the configured portfolio percentage is rejected.
3. Symbol concentration above the configured symbol percentage is rejected.
4. A new symbol that would exceed the maximum open-position count is rejected.
5. An existing symbol does not consume an additional open-position slot.
6. Duplicate symbols in the current-position snapshot are rejected as ambiguous input.
7. Non-positive equity, notional values, or limits are rejected.
8. The result is immutable and deterministic for identical inputs.
9. No broker or network dependency is required.

## Safety boundary

RISK-002 is a portfolio safety gate, not an execution component. It must sit after deterministic trade planning/risk sizing and before any future order-submission boundary.
