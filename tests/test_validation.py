from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.models import Candle
from src.market_data.validation import is_stale, validate_candle


REFERENCE = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)


def candle(**overrides: object) -> Candle:
    values: dict[str, object] = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "timeframe": "15m",
        "timestamp": REFERENCE - timedelta(minutes=5),
        "open": Decimal("100"),
        "high": Decimal("102"),
        "low": Decimal("99"),
        "close": Decimal("101"),
        "volume": 1000,
    }
    values.update(overrides)
    return Candle(**values)


def test_valid_candle_passes() -> None:
    validate_candle(candle())


def test_invalid_ohlc_relationship_is_rejected() -> None:
    with pytest.raises(ValueError, match="high"):
        validate_candle(candle(high=Decimal("100.5")))


def test_non_positive_price_is_rejected() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        validate_candle(candle(low=Decimal("0")))


def test_negative_volume_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        validate_candle(candle(volume=-1))


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_candle(candle(timestamp=datetime(2026, 10, 1, 9, 55)))


def test_fresh_candle_is_not_stale() -> None:
    assert is_stale(candle(), REFERENCE, timedelta(minutes=10)) is False


def test_old_candle_is_stale() -> None:
    old = candle(timestamp=REFERENCE - timedelta(minutes=11))
    assert is_stale(old, REFERENCE, timedelta(minutes=10)) is True


def test_future_candle_timestamp_is_rejected() -> None:
    future = candle(timestamp=REFERENCE + timedelta(seconds=1))
    with pytest.raises(ValueError, match="future"):
        is_stale(future, REFERENCE, timedelta(minutes=10))
