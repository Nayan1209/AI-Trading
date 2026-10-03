# PAPER-003 — Paper Order Reconciliation Specification

## Objective

Provide a deterministic, broker-independent reconciliation boundary for PAPER-002 order records.

## Scope

PAPER-003 compares an expected paper-order sequence with the immutable snapshot held by `PaperOrderLedger`.

The reconciler must:

1. accept only `PaperOrder` expectations;
2. preserve expected sequence order;
3. require exact order-ID coverage;
4. detect missing orders;
5. detect unexpected orders;
6. detect duplicate expected order IDs;
7. verify recorded order status and quantity/fill-price values match the expected records;
8. return an immutable reconciliation result;
9. perform no network, broker, credential, database, or live-execution operations.

## Non-goals

PAPER-003 does not implement:

- live broker reconciliation;
- Groww API calls;
- exchange matching;
- slippage or partial-fill simulation;
- portfolio/P&L accounting;
- persistent storage;
- live order submission.

## Safety

The reconciler is read-only over the in-process paper ledger. A failed reconciliation must be explicit and fail closed through a deterministic result; it must never mutate the ledger.

## Completion Rule

PAPER-003 is complete only after implementation, deterministic tests, documentation, and automatic CI validation are green.
