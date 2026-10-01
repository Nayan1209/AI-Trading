from src.market_data.groww_provider import GrowwMarketDataProvider


class FakeGrowwClient:
    EXCHANGE_NSE = "NSE"
    SEGMENT_CASH = "CASH"

    def get_quote(self, *, exchange, segment, trading_symbol):
        assert exchange == "NSE"
        assert segment == "CASH"
        assert trading_symbol == "RELIANCE"
        return {
            "last_trade_time": 1760000000000,
            "volume": 123456,
            "ohlc": {
                "open": 1400.0,
                "high": 1425.5,
                "low": 1395.0,
                "close": 1418.25,
            },
        }


def test_groww_provider_normalizes_quote_without_network_access():
    provider = GrowwMarketDataProvider("test-token", client=FakeGrowwClient())

    candle = provider.get_latest_candle("RELIANCE")

    assert candle.symbol == "RELIANCE"
    assert candle.exchange == "NSE"
    assert candle.timeframe == "1d_snapshot"
    assert candle.open == 1400
    assert candle.high == 1425.5
    assert candle.low == 1395
    assert candle.close == 1418.25
    assert candle.volume == 123456
    assert candle.timestamp.tzinfo is not None
