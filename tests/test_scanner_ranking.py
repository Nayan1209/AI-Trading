from dataclasses import replace
from decimal import Decimal

import pytest

from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_ranking import ScannerRankingService


def snapshot(
    internal_id: str = "NSE:CASH:RELIANCE",
    symbol: str = "RELIANCE",
    sample_count: int = 3,
    first: str = "100",
    latest: str = "105",
    high: str = "106",
    low: str = "99",
) -> ScannerFeatureSnapshot:
    first_d = Decimal(first)
    latest_d = Decimal(latest)
    return ScannerFeatureSnapshot(
        internal_id=internal_id,
        trading_symbol=symbol,
        sample_count=sample_count,
        first_ltp=first_d,
        latest_ltp=latest_d,
        high_ltp=Decimal(high),
        low_ltp=Decimal(low),
        change_pct=(latest_d - first_d) / first_d * Decimal("100"),
    )


def test_ranking_orders_by_change_then_sample_count_then_id() -> None:
    result = ScannerRankingService().rank(
        [
            snapshot("NSE:CASH:TCS", "TCS", sample_count=4, first="100", latest="105"),
            snapshot("NSE:CASH:INFY", "INFY", sample_count=5, first="100", latest="105"),
            snapshot("NSE:CASH:RELIANCE", sample_count=3, first="100", latest="110"),
        ]
    )

    assert [(item.rank, item.snapshot.internal_id) for item in result] == [
        (1, "NSE:CASH:RELIANCE"),
        (2, "NSE:CASH:INFY"),
        (3, "NSE:CASH:TCS"),
    ]


def test_ranking_uses_internal_id_as_final_tie_breaker() -> None:
    result = ScannerRankingService().rank(
        [
            snapshot("NSE:CASH:TCS", "TCS", sample_count=3),
            snapshot("NSE:CASH:INFY", "INFY", sample_count=3),
        ]
    )

    assert tuple(item.snapshot.internal_id for item in result) == (
        "NSE:CASH:INFY",
        "NSE:CASH:TCS",
    )


def test_ranking_returns_empty_for_empty_input() -> None:
    assert ScannerRankingService().rank(()) == ()


def test_ranking_preserves_quality_gate_fail_closed_behavior() -> None:
    invalid = replace(snapshot(), first_ltp=Decimal("0"))

    with pytest.raises(ValueError, match="prices must be positive"):
        ScannerRankingService().rank((invalid,))


def test_ranking_enforces_configured_minimum_samples() -> None:
    with pytest.raises(ValueError, match="sample_count"):
        ScannerRankingService(min_samples=4).rank((snapshot(sample_count=3),))
