"""Deterministic scanner universe and bounded market-data window."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Sequence

from src.market_data.scanner import ScannerCandidate, ScannerMarketDataService


@dataclass(frozen=True)
class ScannerUniverse:
    """Canonical, deterministic CASH instrument universe for one scanner run."""

    internal_ids: tuple[str, ...]

    @classmethod
    def from_internal_ids(cls, internal_ids: Sequence[str]) -> "ScannerUniverse":
        """Build a sorted, duplicate-free CASH-only scanner universe."""
        normalized = tuple(internal_ids)
        if not normalized:
            raise ValueError("scanner universe must not be empty")

        seen: set[str] = set()
        for internal_id in normalized:
            if not isinstance(internal_id, str) or not internal_id.strip():
                raise ValueError("scanner universe contains an invalid internal_id")
            parts = internal_id.split(":")
            if len(parts) != 3 or any(not part for part in parts):
                raise ValueError("scanner internal_id must be exchange:segment:symbol")
            if parts[1].upper() != "CASH":
                raise ValueError("scanner universe accepts CASH instruments only")
            if internal_id in seen:
                raise ValueError("scanner universe contains duplicate internal_id")
            seen.add(internal_id)

        return cls(tuple(sorted(normalized)))


@dataclass(frozen=True)
class MarketDataWindow:
    """Inclusive, deterministic time window used for scanner market-data reads."""

    reference_time: datetime
    max_age: timedelta

    def __post_init__(self) -> None:
        if self.reference_time.tzinfo is None or self.reference_time.utcoffset() is None:
            raise ValueError("reference_time must be timezone-aware")
        if self.max_age < timedelta(0):
            raise ValueError("max_age must be non-negative")

    @property
    def start_time(self) -> datetime:
        return self.reference_time - self.max_age

    @property
    def end_time(self) -> datetime:
        return self.reference_time

    def contains(self, timestamp: datetime) -> bool:
        """Return whether an event timestamp is inside the inclusive window."""
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("market-data timestamp must be timezone-aware")
        return self.start_time <= timestamp <= self.end_time


class ScannerUniverseService:
    """Apply a deterministic universe and time window to scanner market data."""

    def __init__(self, market_data: ScannerMarketDataService):
        self.market_data = market_data

    def scan(
        self,
        universe: ScannerUniverse,
        window: MarketDataWindow,
    ) -> tuple[ScannerCandidate, ...]:
        """Read only the canonical universe using the supplied bounded window."""
        return self.market_data.scan(
            universe.internal_ids,
            reference_time=window.reference_time,
            max_age=window.max_age,
        )
