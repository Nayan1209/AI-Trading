from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.realtime import ResolvedLtp
from src.market_data.scanner import ScannerMarketDataService
from src.market_data.stream import LtpEvent


REFERENCE = datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc)


def resolved(
    internal_id: str = "NSE:CASH:RELIANCE",
    symbol: str = "RELIANCE",
    segment: str = "CASH",
    timestamp: datetime = REFERENCE - timedelta(seconds=30),
    ltp: str = "149.5",
) -> ResolvedLtp:
    return ResolvedLtp(
        internal_id=internal_id,
        trading_symbol=symbol,
        event=LtpEvent(
            exchange="NSE",
            segment=segment,
            exchange_token="2885",
            timestamp=timestamp,
            ltp=Decimal(ltp),
        ),
    )


class FakeReader:
    def __init__(self, values: dict[str, ResolvedLtp | None]):
        self.values = values
        self.requested: list[str] = []

    def get_latest_ltp(self, internal_id: str) -> ResolvedLtp | None:
        self.requested.append(internal_id)
        return self.values.get(internal_id)


def test_scan_returns_only_fresh_cash_ltp_candidates() -> None:
    reader = FakeReader(
        {
            "NSE:CASH:RELIANCE": resolved(),
            "NSE:CASH:TCS": resolved(
                internal_id="NSE:CASH:TCS",
                symbol="TCS",
                ltp="3100.0",
            ),
            "NSE:CASH:INFY": resolved(
                internal_id="NSE:CASH:INFY",
                symbol="INFY",
                timestamp=REFERENCE - timedelta(minutes=6),
            ),
            "NSE:FNO:RELIANCE": resolved(
                internal_id="NSE:FNO:RELIANCE",
                symbol="RELIANCE",
                segment="FNO",
            ),
        }
    )
    service = ScannerMarketDataService(reader)

    result = service.scan(
        [
            "NSE:CASH:RELIANCE",
            "NSE:CASH:TCS",
            "NSE:CASH:INFY",
            "NSE:FNO:RELIANCE",
        ],
        reference_time=REFERENCE,
        max_age=timedelta(minutes=5),
    )

    assert [candidate.trading_symbol for candidate in result] == ["RELIANCE", "TCS"]
    assert reader.requested == [
        "NSE:CASH:RELIANCE",
        "NSE:CASH:TCS",
        "NSE:CASH:INFY",
        "NSE:FNO:RELIANCE",
    ]


def test_scan_excludes_missing_and_future_data() -> None:
    reader = FakeReader(
        {
            "NSE:CASH:MISSING": None,
            "NSE:CASH:FUTURE": resolved(
                internal_id="NSE:CASH:FUTURE",
                symbol="FUTURE",
                timestamp=REFERENCE + timedelta(seconds=1),
            ),
        }
    )

    result = ScannerMarketDataService(reader).scan(
        ["NSE:CASH:MISSING", "NSE:CASH:FUTURE"],
        reference_time=REFERENCE,
        max_age=timedelta(minutes=5),
    )

    assert result == ()


def test_scan_rejects_reader_identity_mismatch() -> None:
    reader = FakeReader(
        {
            "NSE:CASH:RELIANCE": resolved(
                internal_id="NSE:CASH:TCS",
                symbol="TCS",
            )
        }
    )

    with pytest.raises(ValueError, match="mismatched internal_id"):
        ScannerMarketDataService(reader).scan(
            ["NSE:CASH:RELIANCE"],
            reference_time=REFERENCE,
            max_age=timedelta(minutes=5),
        )


def test_scan_requires_timezone_aware_reference_and_non_negative_age() -> None:
    reader = FakeReader({"NSE:CASH:RELIANCE": resolved()})
    service = ScannerMarketDataService(reader)

    with pytest.raises(ValueError, match="reference_time must be timezone-aware"):
        service.scan(
            ["NSE:CASH:RELIANCE"],
            reference_time=REFERENCE.replace(tzinfo=None),
            max_age=timedelta(minutes=5),
        )

    with pytest.raises(ValueError, match="max_age must be non-negative"):
        service.scan(
            ["NSE:CASH:RELIANCE"],
            reference_time=REFERENCE,
            max_age=timedelta(seconds=-1),
        )
