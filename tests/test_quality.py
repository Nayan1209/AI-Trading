from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.quality import assess_candles, assess_persistence_health
from src.market_data.models import Candle


UTC = timezone.utc
BASE = datetime(2026, 1, 2, 9, 15, tzinfo=UTC)


def candle(offset_minutes: int = 0, **overrides: object) -> Candle:
    values: dict[str, object] = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "timeframe": "15m",
        "timestamp": BASE + timedelta(minutes=offset_minutes),
        "open": Decimal("100"),
        "high": Decimal("102"),
        "low": Decimal("99"),
        "close": Decimal("101"),
        "volume": 1000,
    }
    values.update(overrides)
    return Candle(**values)


def test_quality_report_is_healthy_for_complete_unique_valid_batch() -> None:
    candles = [candle(0), candle(15), candle(30)]

    report = assess_candles(candles, [item.timestamp for item in candles])

    assert report.total_candles == 3
    assert report.unique_candles == 3
    assert report.duplicate_count == 0
    assert report.invalid_count == 0
    assert report.gap_count == 0
    assert report.completeness_ratio == 1.0
    assert report.healthy is True


def test_duplicate_candles_are_reported() -> None:
    first = candle(0)
    report = assess_candles([first, first], [first.timestamp])

    assert report.duplicate_count == 1
    assert report.healthy is False
    assert any("duplicate" in error for error in report.errors)


def test_missing_expected_timestamp_is_reported_as_gap() -> None:
    observed = [candle(0), candle(30)]
    expected = [candle(0).timestamp, candle(15).timestamp, candle(30).timestamp]

    report = assess_candles(observed, expected)

    assert report.gap_count == 1
    assert report.missing_timestamps == (expected[1],)
    assert report.completeness_ratio == pytest.approx(2 / 3)
    assert report.healthy is False


def test_invalid_candle_is_reported_without_stopping_the_batch() -> None:
    invalid = candle(0, high=Decimal("98"))
    valid = candle(15)

    report = assess_candles([invalid, valid])

    assert report.invalid_count == 1
    assert report.healthy is False
    assert any("high must be greater" in error for error in report.errors)


def test_no_expected_timestamps_means_completeness_is_not_assumed_missing() -> None:
    report = assess_candles([candle(0)])

    assert report.completeness_ratio == 1.0
    assert report.gap_count == 0


def test_expected_timestamps_must_be_timezone_aware() -> None:
    naive = datetime(2026, 1, 2, 9, 15)

    with pytest.raises(ValueError, match="timezone-aware"):
        assess_candles([candle(0)], [naive])


def test_persistence_health_reports_success() -> None:
    assert assess_persistence_health(lambda: True) == (True, None)


def test_persistence_health_reports_unhealthy_result() -> None:
    assert assess_persistence_health(lambda: False) == (
        False,
        "persistence health check returned unhealthy",
    )


def test_persistence_health_reports_exception() -> None:
    def broken_check() -> bool:
        raise RuntimeError("database unavailable")

    healthy, error = assess_persistence_health(broken_check)

    assert healthy is False
    assert error == "persistence health check failed: database unavailable"
