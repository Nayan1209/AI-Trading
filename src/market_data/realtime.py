"""Controlled integration of normalized LTP events with market-data state."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, Sequence

from .instruments import InstrumentMaster
from .stream import LtpEvent, normalize_groww_ltp_payload, validate_ltp_freshness


@dataclass(frozen=True)
class ResolvedLtp:
    """An LTP event resolved to the canonical instrument identity."""

    internal_id: str
    trading_symbol: str
    event: LtpEvent


class LtpRepository(Protocol):
    """Persistence boundary for validated, instrument-resolved LTP events."""

    def upsert_ltp(self, events: Sequence[ResolvedLtp]) -> int:
        """Persist events idempotently and return the number of supplied events."""
        ...


class RealtimeLtpService:
    """Resolve, quality-gate and persist Groww LTP payloads without broker coupling."""

    def __init__(self, instrument_master: InstrumentMaster, repository: LtpRepository):
        self.instrument_master = instrument_master
        self.repository = repository

    def ingest_payload(
        self,
        payload: dict[str, object],
        *,
        reference_time: datetime,
        max_age: timedelta,
    ) -> tuple[ResolvedLtp, ...]:
        """Normalize, resolve, freshness-check and persist one LTP payload.

        The operation fails closed: unknown instruments, malformed events, stale
        events and future-dated events are never persisted.
        """
        events = normalize_groww_ltp_payload(payload)
        resolved: list[ResolvedLtp] = []

        for event in events:
            try:
                instrument = self.instrument_master.by_exchange_token(
                    event.exchange, event.exchange_token
                )
            except KeyError as exc:
                raise ValueError(
                    "unknown instrument for exchange/token: "
                    f"{event.exchange}:{event.exchange_token}"
                ) from exc

            if instrument.segment != event.segment:
                raise ValueError(
                    "instrument segment mismatch for exchange/token: "
                    f"{event.exchange}:{event.exchange_token}"
                )

            validate_ltp_freshness(
                event,
                reference_time=reference_time,
                max_age=max_age,
            )
            resolved.append(
                ResolvedLtp(
                    internal_id=instrument.internal_id,
                    trading_symbol=instrument.trading_symbol,
                    event=event,
                )
            )

        self.repository.upsert_ltp(resolved)
        return tuple(resolved)
