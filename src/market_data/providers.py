from datetime import datetime, timezone
from decimal import Decimal
from .models import Candle


class MarketDataProvider:
    def get_latest_candle(self, symbol: str, exchange: str, timeframe: str) -> Candle:
        raise NotImplementedError

    def get_historical_candles(
        self,
        symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int,
    ) -> list[Candle]:
        raise NotImplementedError


class MockMarketDataProvider(MarketDataProvider):
    def get_latest_candle(self, symbol: str, exchange: str, timeframe: str) -> Candle:
        return Candle(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("100.00"),
            high=Decimal("102.00"),
            low=Decimal("99.50"),
            close=Decimal("101.25"),
            volume=100000,
        )

    def get_historical_candles(
        self,
        symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int,
    ) -> list[Candle]:
        return []
