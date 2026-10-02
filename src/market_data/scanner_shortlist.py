"""Deterministic bounded selection of ranked scanner candidates."""

from src.market_data.scanner_ranking import ScannerRankedCandidate


class ScannerCandidateShortlistService:
    """Select a bounded top-N shortlist without changing DATA-015 ranking."""

    def shortlist(
        self,
        ranked: tuple[ScannerRankedCandidate, ...] | list[ScannerRankedCandidate],
        limit: int,
    ) -> tuple[ScannerRankedCandidate, ...]:
        """Return the first ``limit`` valid DATA-015 candidates in rank order."""
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive integer")

        candidates = tuple(ranked)
        seen_ids: set[str] = set()
        for expected_rank, candidate in enumerate(candidates, start=1):
            if candidate.rank != expected_rank:
                raise ValueError("ranked candidates must have contiguous one-based ranks")
            internal_id = candidate.snapshot.internal_id
            if internal_id in seen_ids:
                raise ValueError("ranked candidates must have unique internal_id values")
            seen_ids.add(internal_id)

        return candidates[:limit]
