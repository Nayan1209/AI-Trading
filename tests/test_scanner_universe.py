from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.realtime import ResolvedLtp
from src.market_data.scanner import ScannerMarketDataService
from src.market_data.scanner_universe import MarketDataWindow, ScannerUniverse, ScannerUniverseService
from src.market_data.stream import LtpEvent


REFERENCE = datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc)


def resolved(
    internal_id: str = "NSE:CASH:RELIANCE",
    symbol: str = "RELIANCE",
    timestamp: datetime = REFERENCE - timedelta(seconds=30),
) -> ResolvedLtp:
    return ResolvedLtp(
        internal_id=internal_id,
        trading_symbol=symbol,
        event=LtpEvent(
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
            timestamp=timestamp,
            ltp=Decimal("149.5"),
        ),
    )


class FakeReader:
    def __init__(self, values: dict[str, ResolvedLtp | None]):
        self.values = values
        self.requested: list[str] = []

    def get_latest_ltp(self, internal_id: str) -> ResolvedLtp | None:
        self.requested.append(internal_id)
        return self.values.get(internal_id)


def test_universe_is_cash_only_unique_and_deterministically_sorted() -> None:
    universe = ScannerUniverse.from_internal_ids(
        [
            "NSE:CASH:TCS",
            "NSE:CASH:RELIANCE",
            "BSE:CASH:INFY",
        ]
    )

    assert universe.internal_ids == (
        "BSE:CASH:INFY",
        "NSE:CASH:RELIANCE",
        "NSE:CASH:TCS",
    )


def test_universe_rejects_empty_and_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        ScannerUniverse.from_internal_ids([])

    with pytest.raises(ValueError, match="duplicate internal_id"):
        ScannerUniverse.from_internal_ids(
            ["NSE:CASH:RELIANCE", "NSE:CASH:RELIANCE"]
        )


def test_universe_rejects_non_cash_and_malformed_ids() -> None:
    with pytest.raises(ValueError, match="CASH instruments only"):
        ScannerUniverse.from_internal_ids(["NSE:FNO:RELIANCE"])

    with pytest.raises(ValueError, match="exchange:segment:symbol"):
        ScannerUniverse.from_internal_ids(["NSE:CASH"])


def test_market_data_window_exposes_inclusive_bounds() -> None:
    window = MarketDataWindow(REFERENCE, timedelta(minutes=5))

    assert window.start_time == REFERENCE - timedelta(minutes=5)
    assert window.end_time == REFERENCE
    assert window.contains(window.start_time)
    assert window.contains(window.end_time)
    assert not window.contains(REFERENCE - timedelta(minutes=5, seconds=1))
    assert not window.contains(REFERENCE + timedelta(seconds=1))


def test_market_data_window_rejects_naive_reference_and_negative_age() -> None:
    with pytest.raises(ValueError, match="reference_time must be timezone-aware"):
        MarketDataWindow(REFERENCE.replace(tzinfo=None), timedelta(minutes=5))

    with pytest.raises(ValueError, match="max_age must be non-negative"):
        MarketDataWindow(REFERENCE, timedelta(seconds=-1))


def test_market_data_window_rejects_naive_event_timestamp() -> None:
    window = MarketDataWindow(REFERENCE, timedelta(minutes=5))

    with pytest.raises(ValueError, match="market-data timestamp must be timezone-aware"):
        window.contains(REFERENCE.replace(tzinfo=None))


def test_universe_service_uses_sorted_universe_and_bounded_window() -> None:
    reader = FakeReader(
        {
            "NSE:CASH:TCS": resolved(
                internal_id="NSE:CASH:TCS",
                symbol="TCS",
            ),
            "NSE:CASH:RELIANCE": resolved(
                internal_id="NSE:CASH:RELIANCE",
                symbol="RELIANCE",
            ),
        }
    )
    universe = ScannerUniverse.from_internal_ids(
        ["NSE:CASH:TCS", "NSE:CASH:RELIANCE"]
    )
    window = MarketDataWindow(REFERENCE, timedelta(minutes=5))

    result = ScannerUniverseService(ScannerMarketDataService(reader)).scan(
        universe, window
    )

    assert [candidate.trading_symbol for candidate in result] == ["RELIANCE", "TCS"]
    assert reader.requested == ["NSE:CASH:RELIANCE", "NSE:CASH:TCS"]
