# Reversal Signal Specification

**Document ID:** SIG-001-REVERSAL  
**Status:** Concrete deterministic strategy implemented  
**Parent:** SIG-001 Signal Engine

## Objective

Provide a second concrete SIG-001 strategy using only the validated DATA-016 scanner shortlist and its descriptive percentage-change feature.

## Deterministic Rule

Let `change_pct` be the percentage-change feature carried by the shortlisted candidate.

- Default reversal threshold: `2%`.
- `change_pct > +2%` → `SHORT` reversal signal.
- `change_pct < -2%` → `LONG` reversal signal.
- `-2% <= change_pct <= +2%` → no signal.
- The threshold is configurable but must be strictly positive.
- Strategy score is `abs(change_pct)` capped at `100`.
- The reason code identifies whether the positive or negative reversal threshold was crossed.

The boundary is strict: exactly `+2%` or `-2%` does not produce a signal.

## Contract

Every emitted signal preserves the candidate rank, canonical internal ID and trading symbol, and uses signal type `reversal`. The existing SIG-001 engine validates those identity fields and the score range.

## Safety Boundary

This strategy is an observation-only mean-reversion hypothesis. It does not create quantities, prices, orders, risk overrides, broker calls, AI calls, or execution instructions.

## Acceptance Criteria

- Positive change above the threshold emits a SHORT reversal signal.
- Negative change below the threshold emits a LONG reversal signal.
- Changes at or inside the threshold emit no signal.
- Strategy scores remain within `0..100`.
- Invalid non-positive thresholds are rejected.
- Tests use deterministic in-memory fixtures only.
- No Groww credentials, PostgreSQL service, AI model, or live trading operation is required.
