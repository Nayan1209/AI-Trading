# Scanner Candidate Shortlist Specification
**Document ID:** DATA-016  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Deterministic top-N selection from DATA-015-ranked scanner candidates

## Objective

Add a bounded shortlist boundary after DATA-015. DATA-016 converts the complete deterministic ranking into a caller-defined top-N candidate set for later scanner consumers.

DATA-016 does not generate a buy/sell/hold signal, call an AI model, create a trade plan, size a position, place an order, or connect to a broker.

## Selection Contract

`ScannerCandidateShortlistService` accepts only `ScannerRankedCandidate` values produced by DATA-015 and returns the first `limit` candidates in their existing deterministic rank order.

`limit` must be a positive integer. A limit greater than the ranked candidate count returns all available candidates without inventing or duplicating entries.

The selected candidates retain their original one-based DATA-015 ranks and validated snapshots.

## Fail-Closed Behavior

Invalid limits raise `ValueError`. The service rejects malformed ranked input when ranks are not contiguous one-based integers, duplicate internal IDs are present, or rank order is not ascending.

Empty ranked input is valid and returns an empty tuple.

The shortlist service does not reorder, repair, clamp, discard, or invent candidates.

## Determinism

The same DATA-015 ranked input and limit always produce the same tuple. Selection is positional and never depends on unordered iteration.

## Safety Boundary

DATA-016 is scanner infrastructure only. It introduces no strategy signal, AI decision, trade plan, risk override, broker connection, order placement, withdrawal capability, or live trading behavior.

## Acceptance Criteria

- DATA-015 ranked candidates are the only accepted downstream input contract.
- Positive `limit` is required.
- Selection preserves DATA-015 rank order and original ranks.
- A limit larger than the input returns all candidates.
- Empty input returns an empty tuple.
- Malformed rank sequences fail closed.
- Duplicate candidate identities fail closed.
- Tests require no Groww credentials or production PostgreSQL service.
- README and `brain/12_BUILD_STATUS.md` identify DATA-016 and its CI gate.
