"""Groww-backed market-data adapter.

This module is intentionally read-only. It does not expose order placement.
The adapter converts Groww data into the project's internal Candle model so the
rest of the system does not depend on the broker SDK.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from .models import Candle
from .providers import MarketDataProvider


IST = ZoneInfo("Asia/Kolkata")


class GrowwMarketDataProvider(MarketDataProvider):
    """Read-only market-data provider backed by the Groww Python SDK."""

    def __init__(self, access_token: str, client: Any | None = None) -> None:
        if not access_token:
            raise ValueError("Groww access token is required")

        if client is not None:
            self._client = client
            return

        try:
            from growwapi import GrowwAPI
        except ImportError as exc:  # pragma: no cover - dependency/environment guard
            raise RuntimeError(
                "growwapi is not installed. Install project requirements first."
            ) from exc

        self._client = GrowwAPI(access_token)

    def get_latest_candle(
        self, symbol: str, exchange: str = "NSE", timeframe: str = "1d_snapshot"
    ) -> Candle:
        """Return the current-day OHLC snapshot for one cash instrument.

        Groww's get_quote endpoint returns current-day OHLC plus the last traded
        price, volume and last-trade timestamp. It is not an interval candle.
        Interval candles use the historical-data adapter below.
        """
        exchange_name = getattr(
            self._client, f"EXCHANGE_{exchange.upper()}", exchange.upper()
        )
        segment = getattr(self._client, "SEGMENT_CASH", "CASH")

        quote = self._client.get_quote(
            exchange=exchange_name,
            segment=segment,
            trading_symbol=symbol,
        )

        ohlc = quote.get("ohlc") or {}
        timestamp = _quote_timestamp(quote.get("last_trade_time"))

        return Candle(
            symbol=symbol,
            exchange=exchange.upper(),
            timeframe=timeframe,
            timestamp=timestamp,
            open=Decimal(str(ohlc["open"])),
            high=Decimal(str(ohlc["high"])),
            low=Decimal(str(ohlc["low"])),
            close=Decimal(str(ohlc["close"])),
            volume=int(quote.get("volume", 0)),
        )

    def get_historical_candles(
        self,
        symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int,
    ) -> list[Candle]:
        """Fetch and normalize Groww historical candles.

        ``symbol`` is the Groww symbol from the instrument master, for example
        ``NSE-RELIANCE``. Groww returns timestamps without an explicit timezone
        in the current backtesting API; they are interpreted as India Standard
        Time and normalized to timezone-aware datetimes.
        """
        _validate_range(start_time, end_time, interval_minutes)

        exchange_name = getattr(
            self._client, f"EXCHANGE_{exchange.upper()}", exchange.upper()
        )
        segment = getattr(self._client, "SEGMENT_CASH", "CASH")
        candle_interval = _candle_interval(self._client, interval_minutes)

        response = self._client.get_historical_candles(
            exchange=exchange_name,
            segment=segment,
            groww_symbol=symbol,
            start_time=_format_time(start_time),
            end_time=_format_time(end_time),
            candle_interval=candle_interval,
        )

        return [
            _historical_row_to_candle(
                row,
                groww_symbol=symbol,
                exchange=exchange.upper(),
                interval_minutes=interval_minutes,
            )
            for row in response.get("candles", [])
        ]


def _quote_timestamp(value: object) -> datetime:
    """Convert Groww's epoch-millisecond timestamp to an aware UTC datetime."""
    if value is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)


def _validate_range(start_time: datetime, end_time: datetime, interval_minutes: int) -> None:
    if start_time.tzinfo is None or start_time.utcoffset() is None:
        raise ValueError("start_time must be timezone-aware")
    if end_time.tzinfo is None or end_time.utcoffset() is None:
        raise ValueError("end_time must be timezone-aware")
    if end_time <= start_time:
        raise ValueError("end_time must be after start_time")
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be greater than zero")


def _format_time(value: datetime) -> str:
    return value.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")


def _candle_interval(client: Any, interval_minutes: int) -> str:
    """Use the SDK interval constant when available, with a documented fallback."""
    return str(
        getattr(client, f"CANDLE_INTERVAL_MIN_{interval_minutes}", f"{interval_minutes}minute")
    )


def _historical_row_to_candle(
    row: list[object] | tuple[object, ...],
    groww_symbol: str,
    exchange: str,
    interval_minutes: int,
) -> Candle:
    if len(row) < 6:
        raise ValueError("historical candle row must contain at least 6 values")

    timestamp = _historical_timestamp(row[0])
    return Candle(
        symbol=groww_symbol,
        exchange=exchange,
        timeframe=f"{interval_minutes}m",
        timestamp=timestamp,
        open=Decimal(str(row[1])),
        high=Decimal(str(row[2])),
        low=Decimal(str(row[3])),
        close=Decimal(str(row[4])),
        volume=int(row[5]),
    )


def _historical_timestamp(value: object) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=IST)
    if not isinstance(value, str):
        raise ValueError("historical candle timestamp must be a string or epoch value")

    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("historical candle timestamp is not valid ISO format") from exc

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=IST)
    return parsed
