from datetime import datetime, timedelta

from .models import Candle


def validate_candle(candle: Candle) -> None:
    """Raise ValueError when a normalized candle violates deterministic data rules."""
    if not candle.symbol.strip():
        raise ValueError("symbol must not be empty")
    if not candle.exchange.strip():
        raise ValueError("exchange must not be empty")
    if not candle.timeframe.strip():
        raise ValueError("timeframe must not be empty")
    if candle.timestamp.tzinfo is None or candle.timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    if min(candle.open, candle.high, candle.low, candle.close) <= 0:
        raise ValueError("OHLC prices must be greater than zero")
    if candle.high < max(candle.open, candle.close):
        raise ValueError("high must be greater than or equal to open and close")
    if candle.low > min(candle.open, candle.close):
        raise ValueError("low must be less than or equal to open and close")
    if candle.high < candle.low:
        raise ValueError("high must be greater than or equal to low")
    if candle.volume < 0:
        raise ValueError("volume must be non-negative")
    if candle.last_price is not None and candle.last_price <= 0:
        raise ValueError("last traded price must be greater than zero")


def is_stale(candle: Candle, reference_time: datetime, max_age: timedelta) -> bool:
    """Return whether a validated candle is older than the supplied freshness threshold."""
    if reference_time.tzinfo is None or reference_time.utcoffset() is None:
        raise ValueError("reference_time must be timezone-aware")
    if max_age < timedelta(0):
        raise ValueError("max_age must be non-negative")
    if candle.timestamp.tzinfo is None or candle.timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    if candle.timestamp > reference_time:
        raise ValueError("candle timestamp cannot be in the future")
    return reference_time - candle.timestamp > max_age
