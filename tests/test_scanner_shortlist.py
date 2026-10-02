from decimal import Decimal

import pytest

from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.market_data.scanner_shortlist import ScannerCandidateShortlistService


def candidate(rank: int, internal_id: str) -> ScannerRankedCandidate:
    snapshot = ScannerFeatureSnapshot(
        internal_id=internal_id,
        trading_symbol=internal_id.split(":")[-1],
        sample_count=3,
        first_ltp=Decimal("100"),
        latest_ltp=Decimal("105"),
        high_ltp=Decimal("106"),
        low_ltp=Decimal("99"),
        change_pct=Decimal("5"),
    )
    return ScannerRankedCandidate(rank=rank, snapshot=snapshot)


def test_shortlist_returns_top_n_in_existing_rank_order() -> None:
    ranked = (candidate(1, "NSE:CASH:RELIANCE"), candidate(2, "NSE:CASH:INFY"), candidate(3, "NSE:CASH:TCS"))

    result = ScannerCandidateShortlistService().shortlist(ranked, limit=2)

    assert tuple(item.snapshot.internal_id for item in result) == (
        "NSE:CASH:RELIANCE",
        "NSE:CASH:INFY",
    )
    assert tuple(item.rank for item in result) == (1, 2)


def test_shortlist_returns_all_when_limit_exceeds_count() -> None:
    ranked = (candidate(1, "NSE:CASH:RELIANCE"), candidate(2, "NSE:CASH:INFY"))

    assert ScannerCandidateShortlistService().shortlist(ranked, limit=10) == ranked


def test_shortlist_accepts_empty_input() -> None:
    assert ScannerCandidateShortlistService().shortlist((), limit=5) == ()


@pytest.mark.parametrize("limit", [0, -1, True, False])
def test_shortlist_rejects_non_positive_or_boolean_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        ScannerCandidateShortlistService().shortlist((), limit=limit)


def test_shortlist_rejects_non_contiguous_ranks() -> None:
    ranked = (candidate(1, "NSE:CASH:RELIANCE"), candidate(3, "NSE:CASH:INFY"))

    with pytest.raises(ValueError, match="contiguous one-based"):
        ScannerCandidateShortlistService().shortlist(ranked, limit=2)


def test_shortlist_rejects_duplicate_candidate_identity() -> None:
    ranked = (candidate(1, "NSE:CASH:RELIANCE"), candidate(2, "NSE:CASH:RELIANCE"))

    with pytest.raises(ValueError, match="unique internal_id"):
        ScannerCandidateShortlistService().shortlist(ranked, limit=2)
