from .models import Candle
from .providers import MarketDataProvider

class MarketDataService:
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def latest(self, symbol: str, exchange: str = 'NSE', timeframe: str = '15m') -> Candle:
        return self.provider.get_latest_candle(symbol, exchange, timeframe)
