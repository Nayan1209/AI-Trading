from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.instruments import Instrument, InstrumentMaster
from src.market_data.realtime import RealtimeLtpService


REFERENCE = datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc)


class FakeLtpRepository:
    def __init__(self) -> None:
        self.events = []

    def upsert_ltp(self, events) -> int:
        self.events.extend(events)
        return len(events)


def master() -> InstrumentMaster:
    return InstrumentMaster(
        [
            Instrument(
                internal_id="NSE:CASH:RELIANCE",
                exchange="NSE",
                exchange_token="2885",
                trading_symbol="RELIANCE",
                groww_symbol="RELIANCE",
                instrument_type="EQUITY",
                segment="CASH",
            )
        ]
    )


def payload() -> dict[str, object]:
    return {
        "ltp": {
            "NSE": {
                "CASH": {
                    "2885": {
                        "tsInMillis": 1790932500000,
                        "ltp": 149.5,
                    }
                }
            }
        }
    }


def test_ltp_is_resolved_to_canonical_instrument_and_persisted() -> None:
    repository = FakeLtpRepository()
    service = RealtimeLtpService(master(), repository)

    resolved = service.ingest_payload(
        payload(),
        reference_time=REFERENCE,
        max_age=timedelta(minutes=1),
    )

    assert len(resolved) == 1
    assert resolved[0].internal_id == "NSE:CASH:RELIANCE"
    assert resolved[0].trading_symbol == "RELIANCE"
    assert resolved[0].event.ltp == Decimal("149.5")
    assert tuple(repository.events) == resolved


def test_unknown_exchange_token_fails_closed_and_is_not_persisted() -> None:
    repository = FakeLtpRepository()
    service = RealtimeLtpService(master(), repository)
    unknown = {
        "ltp": {
            "NSE": {
                "CASH": {
                    "999999": {"tsInMillis": 1790932500000, "ltp": 149.5}
                }
            }
        }
    }

    with pytest.raises(ValueError, match="unknown instrument"):
        service.ingest_payload(
            unknown,
            reference_time=REFERENCE,
            max_age=timedelta(minutes=1),
        )

    assert repository.events == []


def test_segment_mismatch_fails_closed() -> None:
    repository = FakeLtpRepository()
    service = RealtimeLtpService(master(), repository)
    mismatched = {
        "ltp": {
            "NSE": {
                "FNO": {
                    "2885": {"tsInMillis": 1790932500000, "ltp": 149.5}
                }
            }
        }
    }

    with pytest.raises(ValueError, match="segment mismatch"):
        service.ingest_payload(
            mismatched,
            reference_time=REFERENCE,
            max_age=timedelta(minutes=1),
        )

    assert repository.events == []


def test_stale_ltp_is_not_persisted() -> None:
    repository = FakeLtpRepository()
    service = RealtimeLtpService(master(), repository)

    with pytest.raises(ValueError, match="stale"):
        service.ingest_payload(
            payload(),
            reference_time=REFERENCE + timedelta(minutes=2),
            max_age=timedelta(seconds=30),
        )

    assert repository.events == []


def test_empty_payload_is_safe_and_persists_nothing() -> None:
    repository = FakeLtpRepository()
    service = RealtimeLtpService(master(), repository)

    resolved = service.ingest_payload(
        {"ltp": {}},
        reference_time=REFERENCE,
        max_age=timedelta(minutes=1),
    )

    assert resolved == ()
    assert repository.events == []
