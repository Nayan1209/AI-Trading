"""Deterministic scanner-ready consumer for persisted market data."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol, Sequence

from src.market_data.realtime import ResolvedLtp


@dataclass(frozen=True)
class ScannerCandidate:
    """Validated market data eligible for downstream scanner logic."""

    internal_id: str
    trading_symbol: str
    exchange: str
    segment: str
    timestamp: datetime
    ltp: Decimal


class ScannerLtpReader(Protocol):
    """Read boundary required by the scanner."""

    def get_latest_ltp(self, internal_id: str) -> ResolvedLtp | None:
        """Return the latest persisted LTP for one canonical instrument."""
        ...


class ScannerMarketDataService:
    """Select scanner-eligible instruments without generating trade signals."""

    def __init__(self, reader: ScannerLtpReader):
        self.reader = reader

    def scan(
        self,
        internal_ids: Sequence[str],
        *,
        reference_time: datetime,
        max_age: timedelta,
    ) -> tuple[ScannerCandidate, ...]:
        """Return deterministic scanner candidates from the DATA-010 read path.

        Eligibility is deliberately narrow:
        - canonical instrument IDs are the only lookup key;
        - only CASH instruments are scanner-ready in the current India-first scope;
        - LTP must be positive;
        - the persisted event must not be future-dated;
        - the persisted event must be no older than ``max_age``.

        Missing or ineligible instruments are excluded rather than invented.
        No signal, ranking, order, or execution decision is made here.
        """
        self._validate_inputs(reference_time, max_age)
        candidates: list[ScannerCandidate] = []

        for internal_id in internal_ids:
            latest = self.reader.get_latest_ltp(internal_id)
            if latest is None:
                continue

            event = latest.event
            if latest.internal_id != internal_id:
                raise ValueError("read boundary returned mismatched internal_id")
            if event.segment != "CASH":
                continue
            if event.timestamp.tzinfo is None or event.timestamp.utcoffset() is None:
                raise ValueError("scanner LTP timestamp must be timezone-aware")
            if event.timestamp > reference_time:
                continue
            if reference_time - event.timestamp > max_age:
                continue
            if event.ltp <= 0:
                continue

            candidates.append(
                ScannerCandidate(
                    internal_id=latest.internal_id,
                    trading_symbol=latest.trading_symbol,
                    exchange=event.exchange,
                    segment=event.segment,
                    timestamp=event.timestamp,
                    ltp=event.ltp,
                )
            )

        return tuple(candidates)

    @staticmethod
    def _validate_inputs(reference_time: datetime, max_age: timedelta) -> None:
        if reference_time.tzinfo is None or reference_time.utcoffset() is None:
            raise ValueError("reference_time must be timezone-aware")
        if max_age < timedelta(0):
            raise ValueError("max_age must be non-negative")
