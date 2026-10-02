from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.realtime import ResolvedLtp
from src.market_data.scanner_features import ScannerFeatureService
from src.market_data.scanner_universe import MarketDataWindow, ScannerUniverse
from src.market_data.stream import LtpEvent


REFERENCE = datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc)


def resolved(
    internal_id: str = "NSE:CASH:RELIANCE",
    symbol: str = "RELIANCE",
    timestamp: datetime = REFERENCE,
    ltp: str = "149.5",
    segment: str = "CASH",
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


class FakeHistoryReader:
    def __init__(self, values: dict[str, list[ResolvedLtp]]):
        self.values = values
        self.requests: list[tuple[str, datetime, datetime]] = []

    def get_ltp(self, internal_id: str, start_time: datetime, end_time: datetime) -> list[ResolvedLtp]:
        self.requests.append((internal_id, start_time, end_time))
        return self.values.get(internal_id, [])


def test_feature_snapshot_is_deterministic_and_uses_bounded_history() -> None:
    reader = FakeHistoryReader(
        {
            "NSE:CASH:RELIANCE": [
                resolved(timestamp=REFERENCE - timedelta(minutes=10), ltp="100"),
                resolved(timestamp=REFERENCE - timedelta(minutes=5), ltp="105"),
                resolved(timestamp=REFERENCE, ltp="110"),
            ],
            "NSE:CASH:TCS": [
                resolved(
                    internal_id="NSE:CASH:TCS",
                    symbol="TCS",
                    timestamp=REFERENCE - timedelta(minutes=3),
                    ltp="200",
                )
            ],
        }
    )
    service = ScannerFeatureService(reader)
    universe = ScannerUniverse.from_internal_ids(
        ["NSE:CASH:TCS", "NSE:CASH:RELIANCE"]
    )
    window = MarketDataWindow(REFERENCE, timedelta(minutes=15))

    snapshots = service.snapshot(universe, window)

    assert [item.internal_id for item in snapshots] == [
        "NSE:CASH:RELIANCE",
        "NSE:CASH:TCS",
    ]
    assert snapshots[0].sample_count == 3
    assert snapshots[0].first_ltp == Decimal("100")
    assert snapshots[0].latest_ltp == Decimal("110")
    assert snapshots[0].high_ltp == Decimal("110")
    assert snapshots[0].low_ltp == Decimal("100")
    assert snapshots[0].change_pct == Decimal("10.0")
    assert reader.requests[0][1] == REFERENCE - timedelta(minutes=15)
    assert reader.requests[0][2] == REFERENCE + timedelta(microseconds=1)


def test_feature_snapshot_excludes_invalid_rows() -> None:
    reader = FakeHistoryReader(
        {
            "NSE:CASH:RELIANCE": [
                resolved(timestamp=REFERENCE + timedelta(seconds=1), ltp="101"),
                resolved(timestamp=REFERENCE - timedelta(minutes=2), ltp="102", segment="FNO"),
                resolved(timestamp=REFERENCE - timedelta(minutes=3), ltp="103"),
            ]
        }
    )
    service = ScannerFeatureService(reader)
    universe = ScannerUniverse.from_internal_ids(["NSE:CASH:RELIANCE"])
    window = MarketDataWindow(REFERENCE, timedelta(minutes=5))

    snapshots = service.snapshot(universe, window)

    assert len(snapshots) == 1
    assert snapshots[0].sample_count == 1
    assert snapshots[0].latest_ltp == Decimal("103")


def test_feature_snapshot_skips_missing_history_and_rejects_zero_window() -> None:
    service = ScannerFeatureService(FakeHistoryReader({}))
    universe = ScannerUniverse.from_internal_ids(["NSE:CASH:RELIANCE"])

    assert service.snapshot(
        universe,
        MarketDataWindow(REFERENCE, timedelta(minutes=5)),
    ) == ()

    with pytest.raises(ValueError, match="max_age must be positive"):
        service.snapshot(universe, MarketDataWindow(REFERENCE, timedelta(0)))
