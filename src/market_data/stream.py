"""Deterministic normalization and safety gating for Groww LTP streams.

The live Groww SDK feed is intentionally kept behind this provider-independent
boundary. No network connection or credential is required here: the module
accepts the normalized payload shape returned by GrowwFeed and converts it into
an internal event model suitable for downstream persistence or aggregation.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True)
class LtpEvent:
    """Validated last-traded-price event from a market-data stream."""

    exchange: str
    segment: str
    exchange_token: str
    timestamp: datetime
    ltp: Decimal


def normalize_groww_ltp(
    payload: Mapping[str, object],
    *,
    exchange: str,
    segment: str,
    exchange_token: str,
) -> LtpEvent:
    """Normalize one Groww LTP payload into the internal event model.

    Groww's feed supplies ``tsInMillis`` and ``ltp`` for each subscribed
    exchange/segment/token. The timestamp is normalized to timezone-aware UTC.
    """
    exchange_name = exchange.strip().upper()
    segment_name = segment.strip().upper()
    token = exchange_token.strip()
    if not exchange_name:
        raise ValueError("exchange must not be empty")
    if not segment_name:
        raise ValueError("segment must not be empty")
    if not token:
        raise ValueError("exchange_token must not be empty")

    timestamp_value = payload.get("tsInMillis")
    ltp_value = payload.get("ltp")
    if timestamp_value is None:
        raise ValueError("tsInMillis is required")
    if ltp_value is None:
        raise ValueError("ltp is required")

    try:
        timestamp = datetime.fromtimestamp(float(timestamp_value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("tsInMillis must be a valid epoch-millisecond value") from exc

    try:
        ltp = Decimal(str(ltp_value))
    except Exception as exc:
        raise ValueError("ltp must be a valid decimal value") from exc

    if ltp <= 0:
        raise ValueError("ltp must be greater than zero")

    return LtpEvent(
        exchange=exchange_name,
        segment=segment_name,
        exchange_token=token,
        timestamp=timestamp,
        ltp=ltp,
    )


def normalize_groww_ltp_payload(payload: Mapping[str, object]) -> list[LtpEvent]:
    """Normalize a complete Groww ``get_ltp``/feed-style nested payload.

    Expected shape is ``ltp -> exchange -> segment -> exchange_token -> event``.
    Unknown or empty top-level branches are ignored; malformed subscribed events
    are rejected rather than silently guessed.
    """
    root = payload.get("ltp")
    if not isinstance(root, Mapping):
        raise ValueError("payload must contain an ltp mapping")

    events: list[LtpEvent] = []
    for exchange, exchange_data in root.items():
        if not isinstance(exchange, str) or not isinstance(exchange_data, Mapping):
            raise ValueError("each exchange entry must contain a mapping")
        for segment, segment_data in exchange_data.items():
            if not isinstance(segment, str) or not isinstance(segment_data, Mapping):
                raise ValueError("each segment entry must contain a mapping")
            for exchange_token, event_payload in segment_data.items():
                if not isinstance(exchange_token, str) or not isinstance(event_payload, Mapping):
                    raise ValueError("each exchange-token entry must contain an event mapping")
                events.append(
                    normalize_groww_ltp(
                        event_payload,
                        exchange=exchange,
                        segment=segment,
                        exchange_token=exchange_token,
                    )
                )
    return events


def validate_ltp_freshness(
    event: LtpEvent,
    *,
    reference_time: datetime,
    max_age: timedelta,
) -> None:
    """Fail closed when an LTP event is future-dated or stale."""
    if reference_time.tzinfo is None or reference_time.utcoffset() is None:
        raise ValueError("reference_time must be timezone-aware")
    if max_age < timedelta(0):
        raise ValueError("max_age must be non-negative")
    if event.timestamp > reference_time:
        raise ValueError("LTP timestamp cannot be in the future")
    if reference_time - event.timestamp > max_age:
        raise ValueError("market-data LTP is stale")
