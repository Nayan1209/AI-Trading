# Software Requirements Specification (SRS)
**Version:** 0.1 | **Status:** Draft

## Functional Requirements
FR-001: Ingest supported Indian equity market data.
FR-002: Maintain an exchange instrument master.
FR-003: Normalize external data into internal schemas.
FR-004: Store historical candles for analysis/backtesting.
FR-005: Detect stale or malformed data.
FR-010: Scan the configured universe.
FR-011: Apply liquidity and data-quality filters.
FR-012: Generate deterministic strategy candidates.
FR-013: Score transparent signal features.
FR-014: Support NO_TRADE.
FR-020: Provide structured candidate context to AI.
FR-021: Require schema-valid AI responses.
FR-022: Store model, prompt and input/output metadata.
FR-023: Prevent AI output from bypassing risk controls.
FR-030: Generate entry, stop, target and invalidation conditions.
FR-031: Calculate position size independently.
FR-032: Validate exposure, loss, concentration and configured limits.
FR-033: Reject invalid or unsafe trade plans.
FR-040: Submit broker orders through an adapter.
FR-041: Track order lifecycle and broker responses.
FR-042: Handle partial fills and rejected orders.
FR-043: Reconcile internal state with broker state.
FR-050: Monitor open positions and orders.
FR-051: Detect stop/target/invalidation events.
FR-052: Generate operational and trading alerts.
FR-053: Support emergency trading halt.
FR-060: Record material decisions and actions.
FR-061: Correlate AI decision → risk decision → order → execution → position → outcome.

## Non-Functional Requirements
Security, observability, idempotency, deterministic risk calculations, versioned APIs/schemas, recoverable failures, and auditability are mandatory.
