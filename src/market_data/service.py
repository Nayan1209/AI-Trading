from datetime import datetime, timedelta, timezone

from .models import Candle
from .providers import MarketDataProvider
from .validation import is_stale, validate_candle


class MarketDataService:
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def latest(
        self,
        symbol: str,
        exchange: str = "NSE",
        timeframe: str = "live",
        max_age: timedelta = timedelta(minutes=5),
        reference_time: datetime | None = None,
    ) -> Candle:
        """Return a provider candle only after deterministic quality checks pass."""
        candle = self.provider.get_latest_candle(symbol, exchange, timeframe)
        validate_candle(candle)

        reference = reference_time or datetime.now(timezone.utc)
        if is_stale(candle, reference, max_age):
            raise ValueError("market-data candle is stale")

        return candle

    def historical(
        self,
        groww_symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int,
    ) -> list[Candle]:
        """Return historical candles only after deterministic validation."""
        candles = self.provider.get_historical_candles(
            groww_symbol,
            exchange,
            start_time,
            end_time,
            interval_minutes,
        )
        for candle in candles:
            validate_candle(candle)
        return candles
