"""Groww-backed market-data adapter.

This module is intentionally read-only. It does not expose order placement.
The adapter converts Groww data into the project's internal Candle model so the
rest of the system does not depend on the broker SDK.
"""

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from .models import Candle
from .providers import MarketDataProvider


IST = ZoneInfo("Asia/Kolkata")


class GrowwMarketDataProvider(MarketDataProvider):
    """Read-only market-data provider backed by the Groww Python SDK."""

    def __init__(
        self,
        access_token: str | None = None,
        client: Any | None = None,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        access_token = (access_token or "").strip()
        if client is not None:
            self._client = client
            return

        try:
            from growwapi import GrowwAPI
        except ImportError as exc:  # pragma: no cover - dependency/environment guard
            raise RuntimeError(
                "growwapi is not installed. Install project requirements first."
            ) from exc

        if not access_token and api_key and api_secret:
            token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
            access_token = token.get("token", "") if isinstance(token, Mapping) else token
        if not isinstance(access_token, str) or not access_token.strip():
            raise ValueError("Groww access token or API key and secret are required")

        self._client = GrowwAPI(access_token)

    def get_latest_candle(
        self, symbol: str, exchange: str = "NSE", timeframe: str = "live"
    ) -> Candle:
        """Return a live quote or a fresh 15-minute candle from Groww."""
        if timeframe == "15m":
            end_time = datetime.now(timezone.utc)
            candles = self.get_historical_candles(
                f"{exchange.upper()}-{symbol}",
                exchange,
                end_time - timedelta(days=1),
                end_time,
                interval_minutes=15,
            )
            if not candles:
                raise ValueError("Groww returned no 15-minute candles for this instrument")
            return candles[-1].model_copy(update={"symbol": symbol})
        if timeframe != "live":
            raise ValueError("timeframe must be 'live' or '15m'")

        exchange_name = getattr(
            self._client, f"EXCHANGE_{exchange.upper()}", exchange.upper()
        )
        segment = getattr(self._client, "SEGMENT_CASH", "CASH")

        response = self._client.get_quote(
            exchange=exchange_name,
            segment=segment,
            trading_symbol=symbol,
            timeout=5,
        )
        quote = _response_payload(response)
        ohlc = quote.get("ohlc")
        if not isinstance(ohlc, Mapping):
            raise ValueError("Groww quote did not include OHLC data")
        last_price = quote.get("last_price")
        if last_price is None:
            raise ValueError("Groww quote did not include a last traded price")
        if "volume" not in quote:
            raise ValueError("Groww quote did not include traded volume")

        return Candle(
            symbol=symbol,
            exchange=exchange.upper(),
            timeframe="live",
            timestamp=_quote_timestamp(quote.get("last_trade_time")),
            open=Decimal(str(ohlc["open"])),
            high=Decimal(str(ohlc["high"])),
            low=Decimal(str(ohlc["low"])),
            close=Decimal(str(ohlc["close"])),
            volume=int(quote["volume"]),
            last_price=Decimal(str(last_price)),
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
        current_method = getattr(self._client, "get_historical_candles", None)
        if callable(current_method):
            candle_interval = _candle_interval(self._client, interval_minutes)
            response = current_method(
                exchange=exchange_name,
                segment=segment,
                groww_symbol=symbol,
                start_time=_format_time(start_time),
                end_time=_format_time(end_time),
                candle_interval=candle_interval,
                timeout=5,
            )
        else:
            legacy_method = getattr(self._client, "get_historical_candle_data", None)
            if not callable(legacy_method):
                raise RuntimeError("Installed Groww SDK has no historical candle method")
            legacy_method_name = _trading_symbol(symbol, exchange)
            response = legacy_method(
                trading_symbol=legacy_method_name,
                exchange=exchange_name,
                segment=segment,
                start_time=_format_time(start_time),
                end_time=_format_time(end_time),
                interval_in_minutes=interval_minutes,
                timeout=5,
            )

        payload = _response_payload(response)

        return [
            _historical_row_to_candle(
                row,
                groww_symbol=symbol,
                exchange=exchange.upper(),
                interval_minutes=interval_minutes,
            )
            for row in payload.get("candles", [])
        ]


def _response_payload(response: object) -> Mapping[str, Any]:
    if not isinstance(response, Mapping):
        raise ValueError("Groww returned an unexpected market-data response")
    payload = response.get("payload", response)
    if not isinstance(payload, Mapping):
        raise ValueError("Groww returned an unexpected market-data payload")
    return payload


def _trading_symbol(groww_symbol: str, exchange: str) -> str:
    prefix = f"{exchange.upper()}-"
    return groww_symbol[len(prefix) :] if groww_symbol.upper().startswith(prefix) else groww_symbol


def _quote_timestamp(value: object) -> datetime:
    """Convert Groww's epoch-millisecond timestamp without inventing a fallback."""
    if value is None:
        raise ValueError("Groww quote did not include a last-trade timestamp")
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Groww returned an invalid last-trade timestamp") from exc


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
