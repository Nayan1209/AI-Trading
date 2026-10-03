# EXEC-003 — Controlled Deployment Authorization

**Status:** Implementation started; no live broker submission is enabled.

## Purpose

EXEC-003 defines the final deterministic authorization boundary before a controlled deployment can be considered. It consumes verified EXEC-002 runtime readiness plus explicit operational evidence, but it does not place orders or enable broker submission.

## Required evidence

The caller must provide:

1. EXEC-002 runtime readiness has passed.
2. A successful paper/simulation verification result is present.
3. An explicit operator approval is present.
4. A rollback plan is ready.
5. The independent kill switch remains ready.
6. The execution lock remains enabled until the deployment decision is handed to the separately controlled submission layer.

## Design rules

- Failed prerequisites fail closed.
- No broker API is called.
- No credentials, tokens, or TOTP values are read or persisted.
- Authorization is immutable and records reasons for rejection.
- This gate does not itself enable live trading.
- PLAN-001, RISK-001, RISK-002, EXEC-001, and EXEC-002 remain mandatory upstream controls.

## Safety boundary

A passing EXEC-003 result means the deployment evidence is complete. It is not an order authorization and cannot be used by itself to submit a real-money order.

## Test boundary

Tests use deterministic booleans and synthetic identifiers only. No broker network, credentials, or real order submission are involved.
