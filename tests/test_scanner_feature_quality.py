from dataclasses import replace
from decimal import Decimal

import pytest

from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_feature_quality import ScannerFeatureQualityGate


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


def test_quality_gate_accepts_valid_features_and_sorts_ids() -> None:
    gate = ScannerFeatureQualityGate()
    result = gate.validate(
        [
            snapshot("NSE:CASH:TCS", "TCS"),
            snapshot("NSE:CASH:RELIANCE"),
        ]
    )

    assert tuple(item.internal_id for item in result) == (
        "NSE:CASH:RELIANCE",
        "NSE:CASH:TCS",
    )


def test_quality_gate_enforces_minimum_samples() -> None:
    gate = ScannerFeatureQualityGate(min_samples=3)

    with pytest.raises(ValueError, match="sample_count"):
        gate.validate((snapshot(sample_count=2),))


def test_quality_gate_rejects_non_positive_prices() -> None:
    gate = ScannerFeatureQualityGate()

    with pytest.raises(ValueError, match="prices must be positive"):
        gate.validate((snapshot(first="0"),))


def test_quality_gate_rejects_inconsistent_change() -> None:
    gate = ScannerFeatureQualityGate()
    invalid = replace(snapshot(), change_pct=Decimal("4"))

    with pytest.raises(ValueError, match="change_pct"):
        gate.validate((invalid,))


def test_quality_gate_rejects_duplicate_internal_ids() -> None:
    gate = ScannerFeatureQualityGate()

    with pytest.raises(ValueError, match="duplicate internal_id"):
        gate.validate((snapshot(), snapshot()))


def test_quality_gate_requires_positive_minimum_samples() -> None:
    with pytest.raises(ValueError, match="min_samples"):
        ScannerFeatureQualityGate(min_samples=0)
