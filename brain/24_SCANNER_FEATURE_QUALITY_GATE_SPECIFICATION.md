# Scanner Feature Quality Gate Specification
**Document ID:** DATA-014  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Fail-closed validation of DATA-013 scanner feature snapshots before downstream scanner consumption

## Objective

Add a deterministic quality boundary between the descriptive DATA-013 feature snapshot and future scanner/ranking logic. DATA-014 validates that a feature snapshot is internally coherent before it can be consumed downstream.

DATA-014 does not rank instruments, generate trading signals, call AI models, create trade plans, place orders, or execute trades.

## Quality Contract

`ScannerFeatureQualityGate` validates:

- non-empty canonical `internal_id` and trading symbol;
- unique `internal_id` values within one snapshot batch;
- caller-defined minimum sample count;
- strictly positive first/latest/high/low LTP values;
- `high_ltp >= low_ltp`;
- exact `Decimal` consistency of `change_pct` with first/latest LTP.

The gate returns accepted snapshots in deterministic lexical `internal_id` order.

## Fail-Closed Behavior

Invalid input is rejected with `ValueError`. The gate does not repair, clamp, invent, or silently discard a malformed snapshot. This keeps downstream scanner logic from acting on contradictory descriptive data.

An empty snapshot collection is valid and returns an empty tuple; DATA-013 already defines missing market history as absence of a snapshot.

## Safety Boundary

DATA-014 remains scanner data-quality infrastructure only. It introduces no strategy score, signal, AI decision, trade plan, risk override, broker connection, order placement, withdrawal capability, or live trading behavior.

## Acceptance Criteria

- DATA-013 `ScannerFeatureSnapshot` is the only feature input contract.
- Validation uses `Decimal` arithmetic without float conversion.
- Duplicate identities fail closed.
- Configured minimum sample requirements are enforced.
- Non-positive prices fail closed.
- High/low relationships fail closed.
- Percentage-change arithmetic is checked exactly.
- Output ordering is deterministic.
- Tests require no Groww credentials or production PostgreSQL service.
- README and build-status documentation identify DATA-014 and its CI gate.
