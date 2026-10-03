# Paper Execution Session Specification
**Version:** 1.0  
**Milestone:** PAPER-004  
**Parent:** Phase 6 — Paper Execution  
**Depends on:** PAPER-001, PAPER-002, PAPER-003

## Purpose

PAPER-004 composes the existing paper-execution boundaries into one deterministic session. A session executes an already-approved `TradePlan`, records the resulting immutable `PaperOrder` in the in-process ledger, and performs a read-only reconciliation over the complete expected session history.

## Contract

The session MUST:

1. accept only an existing `TradePlan` through the PAPER-001 execution boundary;
2. use the `paper` environment enforced by PAPER-001;
3. preserve the immutable `PaperOrder` returned by PAPER-001;
4. record the order exactly once through PAPER-002;
5. build the expected history from the pre-session ledger snapshot plus the new order;
6. reconcile the ledger through PAPER-003 without mutating it;
7. return an immutable `PaperExecutionSessionResult` containing the order and reconciliation result.

## Determinism

For the same initial ledger state, trade plan, and fill price, the session MUST produce the same simulated order and reconciliation result.

## Safety

PAPER-004 MUST NOT:

- call Groww or another broker;
- access broker credentials, API keys, secrets, or TOTP values;
- use network transport;
- enable live trading;
- modify the production execution lock;
- introduce database persistence;
- introduce exchange matching, slippage, or partial fills;
- mutate the reconciliation result or recorded `PaperOrder` values.

## Flow

```text
Approved TradePlan
      ↓
PAPER-001 Paper Execution
      ↓
Immutable PaperOrder
      ↓
PAPER-002 Order Ledger
      ↓
Expected Session History
      ↓
PAPER-003 Read-only Reconciliation
      ↓
Immutable PaperExecutionSessionResult
```

## Completion Rule

PAPER-004 is complete only after implementation, deterministic tests, documentation, and automatic CI validation are green.
