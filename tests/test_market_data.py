from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.models import Candle
from src.market_data.providers import MarketDataProvider
from src.market_data.service import MarketDataService


REFERENCE = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)


class FixedMarketDataProvider(MarketDataProvider):
    def __init__(self, candle: Candle):
        self.candle = candle

    def get_latest_candle(self, symbol: str, exchange: str, timeframe: str) -> Candle:
        return self.candle


def make_candle(timestamp: datetime) -> Candle:
    return Candle(
        symbol="RELIANCE",
        exchange="NSE",
        timeframe="15m",
        timestamp=timestamp,
        open=Decimal("100"),
        high=Decimal("102"),
        low=Decimal("99"),
        close=Decimal("101"),
        volume=1000,
    )


def test_market_data_service_returns_provider_result_without_synthetic_fallback():
    candle = make_candle(REFERENCE - timedelta(minutes=5))
    candle.last_price = Decimal("101.5")
    result = MarketDataService(FixedMarketDataProvider(candle)).latest(
        "RELIANCE", reference_time=REFERENCE
    )
    assert result is candle
    assert result.last_price == Decimal("101.5")


def test_market_data_service_rejects_stale_candle():
    stale = make_candle(REFERENCE - timedelta(minutes=11))
    service = MarketDataService(FixedMarketDataProvider(stale))

    with pytest.raises(ValueError, match="stale"):
        service.latest("RELIANCE", max_age=timedelta(minutes=10), reference_time=REFERENCE)


def test_market_data_service_accepts_fresh_candle():
    fresh = make_candle(REFERENCE - timedelta(minutes=5))
    service = MarketDataService(FixedMarketDataProvider(fresh))

    result = service.latest("RELIANCE", max_age=timedelta(minutes=10), reference_time=REFERENCE)
    assert result is fresh
