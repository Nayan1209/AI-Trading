# Scanner Candidate Ranking Specification
**Document ID:** DATA-015  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Deterministic ordering of DATA-014-approved scanner feature snapshots

## Objective

Add the first downstream scanner ordering boundary after DATA-014. DATA-015 turns validated descriptive feature snapshots into a deterministic ranked list for later scanner consumers.

DATA-015 does not generate a buy/sell/hold signal, call an AI model, create a trade plan, size a position, place an order, or connect to a broker.

## Ranking Contract

`ScannerRankingService` accepts only `ScannerFeatureSnapshot` values and first applies the DATA-014 quality gate.

Candidates are ordered by:

1. `change_pct` descending;
2. `sample_count` descending when percentage change is equal;
3. `internal_id` ascending as the final deterministic tie-breaker.

Ranks are one-based and assigned after the complete deterministic ordering is established.

The output contains the rank and the original validated `ScannerFeatureSnapshot`; no new predictive score is invented.

## Fail-Closed Behavior

Any DATA-014 validation failure remains a `ValueError` and prevents a partial ranked result from being returned. Empty input is valid and returns an empty tuple.

The ranking service does not repair, clamp, discard, or invent feature values.

## Determinism

The same validated input set produces the same ordering regardless of input iteration order. Decimal feature values are compared directly without float conversion.

## Safety Boundary

DATA-015 is scanner infrastructure only. It introduces no strategy signal, AI decision, trade plan, risk override, broker connection, order placement, withdrawal capability, or live trading behavior.

## Acceptance Criteria

- DATA-014 remains the mandatory quality boundary before ranking.
- Ranking is deterministic and stable under input reordering.
- Percentage change is the primary ordering field.
- Sample count is the secondary ordering field.
- Internal ID is the final tie-breaker.
- Ranks are one-based and contiguous.
- Empty input returns an empty tuple.
- Invalid DATA-014 snapshots fail closed.
- Tests require no Groww credentials or production PostgreSQL service.
- README and `brain/12_BUILD_STATUS.md` identify DATA-015 and its CI gate.
