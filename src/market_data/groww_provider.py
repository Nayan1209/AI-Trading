"""Groww-backed market-data adapter.

This module is intentionally read-only. It does not expose order placement.
The adapter converts Groww's quote response into the project's internal Candle
model so the rest of the system does not depend on the broker SDK.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from .models import Candle
from .providers import MarketDataProvider


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
        Interval candles will be implemented through the historical-data adapter.
        """
        exchange_name = getattr(self._client, f"EXCHANGE_{exchange.upper()}", exchange.upper())
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


def _quote_timestamp(value: object) -> datetime:
    """Convert Groww's epoch-millisecond timestamp to an aware UTC datetime."""
    if value is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
