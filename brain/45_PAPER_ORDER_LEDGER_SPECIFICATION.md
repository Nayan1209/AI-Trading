# Paper Order Ledger Specification
**Version:** 1.0  
**Milestone:** PAPER-002  
**Parent:** Phase 6 — Paper Execution  
**Depends on:** PAPER-001

## Purpose

PAPER-002 adds a deterministic in-process ledger for completed PAPER-001 simulated orders. It provides an auditable order history and idempotent order recording without introducing a database, broker, network transport, credentials, or live execution.

## Inputs

The ledger accepts only a valid immutable `PaperOrder` produced by the PAPER-001 paper execution boundary.

## Deterministic Behavior

For each new order:

- the exact `PaperOrder` is appended once;
- insertion order is preserved;
- the order identifier is unique within the ledger;
- retrieval by order ID returns the original immutable order;
- a snapshot returns an immutable tuple of recorded orders.

## Rejections

The ledger must reject:

- non-`PaperOrder` values;
- duplicate order identifiers.

Duplicate recording must fail closed rather than silently creating a second execution record.

## Safety

PAPER-002:

- does not call Groww;
- does not access credentials, access tokens, TOTP values, or secrets;
- does not use network transport;
- does not enable live trading;
- does not modify the production execution lock;
- does not persist data outside the process.

## Non-Goals

PAPER-002 does not implement:

- database persistence;
- exchange matching;
- slippage modelling;
- partial-fill simulation;
- portfolio/P&L accounting;
- broker reconciliation;
- live order submission.

Those remain separate milestones.

## Completion Criteria

PAPER-002 is complete only when implementation, deterministic tests, documentation, and automatic CI validation are green.
