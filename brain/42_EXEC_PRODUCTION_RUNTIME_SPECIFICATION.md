# EXEC-002 — Static-IP Production Runtime

**Status:** Implementation started; no live broker submission is enabled.

## Purpose

EXEC-002 defines the deterministic readiness gate for a controlled production runtime before any real-money Groww execution can be considered.

## Required evidence

The runtime must provide caller-supplied, independently verified evidence for:

1. Production environment selection.
2. Registered static public IP.
3. Observed public IP matching the registered static IP.
4. Execution lock remaining enabled until all readiness checks pass.
5. An independently available kill switch/trading halt.
6. A configured credential reference without storing the credential, token, TOTP, or secret in source control.

## Design rules

- No network discovery is performed by the deterministic gate.
- No broker API is called.
- No credentials are read or persisted.
- A failed prerequisite fails closed.
- Runtime readiness does not itself authorize an order.
- PLAN-001, RISK-001, RISK-002, and EXEC-001 remain mandatory upstream controls.
- The execution lock must remain enabled while readiness is being evaluated.

## Production boundary

Groww production order placement requires a controlled runtime with a registered static public IP. A personal dynamic-network address is not an acceptable production endpoint.

EXEC-002 verifies readiness evidence; it does not turn on live trading. A later controlled-deployment milestone must explicitly authorize production submission after operational verification.

## Test boundary

Tests use synthetic documentation IP addresses and booleans only. No real IP discovery, broker credential, access token, or order submission is used.
