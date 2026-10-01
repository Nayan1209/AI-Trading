from src.market_data.providers import MockMarketDataProvider
from src.market_data.service import MarketDataService

def test_mock_market_data_is_valid():
    candle = MarketDataService(MockMarketDataProvider()).latest('RELIANCE')
    assert candle.symbol == 'RELIANCE'
    assert candle.exchange == 'NSE'
    assert candle.volume >= 0
    assert candle.high >= candle.low
