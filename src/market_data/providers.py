from datetime import datetime
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
