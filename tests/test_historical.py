from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.groww_provider import GrowwMarketDataProvider
from src.market_data.models import Candle
from src.market_data.service import MarketDataService


START = datetime(2026, 9, 30, 9, 15, tzinfo=timezone.utc)
END = START + timedelta(hours=1)


class FakeGrowwClient:
    EXCHANGE_NSE = "NSE"
    SEGMENT_CASH = "CASH"
    CANDLE_INTERVAL_MIN_5 = "5minute"

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def get_historical_candles(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return {
            "candles": [
                ["2026-09-30T14:45:00", 100.0, 102.0, 99.5, 101.0, 1000, None],
                ["2026-09-30T14:50:00", 101.0, 103.0, 100.5, 102.5, 1200, None],
            ]
        }


def test_groww_historical_candles_are_normalized() -> None:
    client = FakeGrowwClient()
    provider = GrowwMarketDataProvider("test-token", client=client)

    candles = provider.get_historical_candles(
        "NSE-RELIANCE", "NSE", START, END, interval_minutes=5
    )

    assert len(candles) == 2
    assert candles[0].symbol == "NSE-RELIANCE"
    assert candles[0].timeframe == "5m"
    assert candles[0].timestamp.tzinfo is not None
    assert candles[0].open == Decimal("100.0")
    assert candles[1].volume == 1200
    assert client.calls[0]["groww_symbol"] == "NSE-RELIANCE"
    assert client.calls[0]["candle_interval"] == "5minute"


def test_historical_service_validates_every_candle() -> None:
    class FixedProvider:
        def get_historical_candles(self, *args: object, **kwargs: object) -> list[Candle]:
            return [
                Candle(
                    symbol="NSE-RELIANCE",
                    exchange="NSE",
                    timeframe="5m",
                    timestamp=START,
                    open=Decimal("100"),
                    high=Decimal("102"),
                    low=Decimal("99"),
                    close=Decimal("101"),
                    volume=1000,
                )
            ]

        def get_latest_candle(self, *args: object, **kwargs: object) -> Candle:
            raise NotImplementedError

    candles = MarketDataService(FixedProvider()).historical(
        "NSE-RELIANCE", "NSE", START, END, 5
    )

    assert candles[0].close == Decimal("101")


def test_historical_range_must_be_valid() -> None:
    provider = GrowwMarketDataProvider("test-token", client=FakeGrowwClient())

    with pytest.raises(ValueError, match="end_time"):
        provider.get_historical_candles(
            "NSE-RELIANCE", "NSE", END, START, interval_minutes=5
        )
