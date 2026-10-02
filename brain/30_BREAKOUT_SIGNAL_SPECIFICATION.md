# Breakout Signal Specification

**Document ID:** SIG-001-BREAKOUT  
**Status:** Concrete deterministic strategy implemented  
**Parent:** SIG-001 Signal Engine

## Objective

Add the next concrete SIG-001 strategy after momentum and reversal using only the validated DATA-016 scanner shortlist and its descriptive price features.

## Deterministic Rule

Let `latest_ltp`, `high_ltp`, `low_ltp`, and `change_pct` be the validated features carried by the shortlisted candidate.

- Default breakout threshold: `1%`.
- A positive `change_pct` strictly above `+1%` with `latest_ltp == high_ltp` produces a `LONG` breakout observation.
- A negative `change_pct` strictly below `-1%` with `latest_ltp == low_ltp` produces a `SHORT` breakout observation.
- If the latest price is not at the corresponding observed extreme, no breakout signal is emitted.
- Changes at or inside the threshold produce no signal.
- The threshold is configurable but must be strictly positive.
- Strategy score is `abs(change_pct)` capped at `100`.
- Reason codes identify whether the high or low breakout condition was met.

The threshold is strict: exactly `+1%` or `-1%` does not produce a signal.

## Contract

Every emitted signal preserves the candidate rank, canonical internal ID and trading symbol, and uses signal type `breakout`. The existing SIG-001 engine validates those identity fields and the score range.

## Safety Boundary

This strategy is an observation-only breakout hypothesis. It does not create quantities, prices, orders, risk overrides, broker calls, AI calls, or execution instructions.

## Acceptance Criteria

- Positive change above the threshold with the latest LTP at the observed high emits a LONG breakout signal.
- Negative change below the threshold with the latest LTP at the observed low emits a SHORT breakout signal.
- A threshold-crossing change without an extreme-price match emits no signal.
- Changes at or inside the threshold emit no signal.
- Strategy scores remain within `0..100`.
- Invalid non-positive thresholds are rejected.
- Tests use deterministic in-memory fixtures only.
- No Groww credentials, PostgreSQL service, AI model, or live trading operation is required.
