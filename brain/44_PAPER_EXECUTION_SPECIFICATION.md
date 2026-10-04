# Paper Execution Boundary Specification
**Version:** 1.0
**Milestone:** PAPER-001
**Parent:** Phase 6 — Paper Execution
**Depends on:** PLAN-001, RISK-002, EXEC-001, EXEC-003

## Purpose

PAPER-001 provides a broker-independent, deterministic paper-execution boundary. It converts an already-approved `TradePlan` into a simulated order/fill without calling Groww, reading credentials, placing live orders, or changing the production execution lock.

## Environment Safety

- Only the explicit `paper` environment is accepted.
- Development, staging, and production are rejected by this boundary.
- No broker/network transport is permitted.
- No credentials, access tokens, TOTP values, or secrets are required.

## Inputs

The executor receives:

1. An immutable PLAN-001 `TradePlan`.
2. A positive simulated fill price.
3. An explicit paper environment.

The plan is assumed to have already passed the deterministic risk and portfolio gates. PAPER-001 does not weaken or replace those gates.

## Deterministic Behavior

For a valid BUY or SELL plan:

- quantity is preserved exactly;
- side is derived from the plan decision;
- fill price is the supplied simulation price;
- status is `FILLED`;
- `internal_id`, `trading_symbol`, and `client_order_id` are preserved from the plan;
- the deterministic order identifier is a SHA-256 prefix derived from canonical plan identity, plan values, and the supplied fill price;
- no external state is read or written.

Executing the same immutable `TradePlan` with the same fill price produces the same order identifier.

## Rejections

The executor must reject:

- non-`paper` environments;
- non-BUY/SELL decisions;
- zero or negative quantity;
- zero or negative simulated fill price;
- malformed plans or plans missing canonical instrument or client order identity.

## Non-Goals

PAPER-001 does not implement:

- live broker submission;
- Groww authentication;
- market-data polling;
- realistic exchange matching;
- slippage modelling;
- partial-fill simulation;
- portfolio persistence;
- reconciliation.

Those are later milestones and must not be smuggled into the first paper boundary.

## Completion Criteria

PAPER-001 is complete only when the implementation, deterministic tests, documentation, and automatic CI validation are green.
