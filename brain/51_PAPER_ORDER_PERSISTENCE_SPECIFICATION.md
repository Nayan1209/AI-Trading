# PAPER-008 — Persistent Paper Order Journal

**Status:** Planned · **Parent:** Phase 6 — Paper Execution
**Depends on:** PLAN-001, PAPER-001, PAPER-002, PAPER-004, DATA-006

## Objective

Add durable, append-only storage for completed immutable paper fills. The journal preserves order and instrument identity across process restarts and provides a deterministic read path for paper-order history.

## Scope

PAPER-008 introduces a PostgreSQL repository and schema migration for `PaperOrder` records. A journal instance represents one paper execution context; multi-account and multi-strategy partitioning are outside this milestone.

The journal stores:

- `order_id` and `client_order_id`;
- `internal_id` and `trading_symbol`;
- decision, quantity, fill price, and status;
- the order timestamp in UTC.

## Contract

The repository must:

1. Accept only immutable, completed `PaperOrder` records with valid order, client-order, and instrument identities.
2. Use fixed-precision PostgreSQL numeric storage for prices and timezone-aware timestamps for event times.
3. Enforce unique `order_id` and unique `client_order_id` within a journal.
4. Insert each order atomically and never update or delete a recorded order.
5. Treat a repeated identity with the same business payload as an idempotent replay and return the original stored record. Exclude the newly generated record timestamp from payload comparison; the first stored timestamp remains authoritative.
6. Reject an identity collision when the business payload differs.
7. Support deterministic lookup by `order_id` or `client_order_id` and deterministic history ordering by timestamp, then `order_id`.
8. Roll back a failed write without leaving a partial journal record.

## Acceptance criteria

- A versioned migration creates the paper-order table and lookup constraints/indexes.
- Valid filled paper orders can be inserted and read back without changing their business fields.
- Replaying the same order is idempotent; changed payloads and conflicting client IDs are rejected.
- Invalid or non-filled order records are rejected before persistence.
- Repository and migration tests cover insert, read, ordering, duplicate, conflict, and rollback behavior.
- The full automated CI suite passes.

## Safety boundary

PAPER-008 is storage only. It does not:

- call Groww or another broker;
- submit, modify, or cancel orders;
- access credentials or secrets;
- use market-data network transports;
- persist position snapshots or portfolio valuations;
- add exchange matching, slippage, partial fills, fees, or short selling;
- enable live execution.

Position persistence and portfolio analytics remain later work. The existing execution lock and deployment authorization requirements remain unchanged.
