from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.stream import (
    LtpEvent,
    normalize_groww_ltp,
    normalize_groww_ltp_payload,
    validate_ltp_freshness,
)


REFERENCE = datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc)


def test_normalize_single_groww_ltp_event() -> None:
    event = normalize_groww_ltp(
        {"tsInMillis": 1790932500000, "ltp": 149.5},
        exchange="nse",
        segment="cash",
        exchange_token="2885",
    )

    assert isinstance(event, LtpEvent)
    assert event.exchange == "NSE"
    assert event.segment == "CASH"
    assert event.exchange_token == "2885"
    assert event.ltp == Decimal("149.5")
    assert event.timestamp.tzinfo == timezone.utc


def test_normalize_nested_groww_ltp_payload() -> None:
    payload = {
        "ltp": {
            "NSE": {
                "CASH": {
                    "2885": {"tsInMillis": 1790932500000, "ltp": 149.5},
                    "1333": {"tsInMillis": 1790932501000, "ltp": 2510.25},
                }
            }
        }
    }

    events = normalize_groww_ltp_payload(payload)

    assert len(events) == 2
    assert [event.exchange_token for event in events] == ["2885", "1333"]


def test_ltp_requires_positive_price() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        normalize_groww_ltp(
            {"tsInMillis": 1790932500000, "ltp": 0},
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
        )


def test_ltp_requires_timestamp_and_price() -> None:
    with pytest.raises(ValueError, match="tsInMillis is required"):
        normalize_groww_ltp(
            {"ltp": 149.5},
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
        )

    with pytest.raises(ValueError, match="ltp is required"):
        normalize_groww_ltp(
            {"tsInMillis": 1790932500000},
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
        )


def test_ltp_freshness_gate_accepts_fresh_event() -> None:
    event = LtpEvent(
        exchange="NSE",
        segment="CASH",
        exchange_token="2885",
        timestamp=REFERENCE - timedelta(seconds=2),
        ltp=Decimal("149.5"),
    )

    validate_ltp_freshness(event, reference_time=REFERENCE, max_age=timedelta(seconds=5))


def test_ltp_freshness_gate_rejects_stale_event() -> None:
    event = LtpEvent(
        exchange="NSE",
        segment="CASH",
        exchange_token="2885",
        timestamp=REFERENCE - timedelta(seconds=6),
        ltp=Decimal("149.5"),
    )

    with pytest.raises(ValueError, match="stale"):
        validate_ltp_freshness(event, reference_time=REFERENCE, max_age=timedelta(seconds=5))


def test_ltp_freshness_gate_rejects_future_event() -> None:
    event = LtpEvent(
        exchange="NSE",
        segment="CASH",
        exchange_token="2885",
        timestamp=REFERENCE + timedelta(seconds=1),
        ltp=Decimal("149.5"),
    )

    with pytest.raises(ValueError, match="future"):
        validate_ltp_freshness(event, reference_time=REFERENCE, max_age=timedelta(seconds=5))


def test_nested_payload_rejects_malformed_event_instead_of_guessing() -> None:
    payload = {
        "ltp": {
            "NSE": {"CASH": {"2885": {"tsInMillis": 1790932500000}}}
        }
    }

    with pytest.raises(ValueError, match="ltp is required"):
        normalize_groww_ltp_payload(payload)
