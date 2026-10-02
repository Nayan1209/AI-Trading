"""Deterministic scanner feature snapshot from bounded persisted LTP history."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Protocol

from src.market_data.realtime import ResolvedLtp
from src.market_data.scanner_universe import MarketDataWindow, ScannerUniverse


@dataclass(frozen=True)
class ScannerFeatureSnapshot:
    """Provider-independent descriptive features for one scanner candidate."""

    internal_id: str
    trading_symbol: str
    sample_count: int
    first_ltp: Decimal
    latest_ltp: Decimal
    high_ltp: Decimal
    low_ltp: Decimal
    change_pct: Decimal


class ScannerLtpHistoryReader(Protocol):
    """Read boundary required for deterministic scanner feature extraction."""

    def get_ltp(
        self,
        internal_id: str,
        start_time,
        end_time,
    ) -> list[ResolvedLtp]:
        """Return persisted LTP events in chronological order for a bounded range."""
        ...


class ScannerFeatureService:
    """Build descriptive scanner features without generating trading signals."""

    def __init__(self, reader: ScannerLtpHistoryReader):
        self.reader = reader

    def snapshot(
        self,
        universe: ScannerUniverse,
        window: MarketDataWindow,
    ) -> tuple[ScannerFeatureSnapshot, ...]:
        """Return deterministic LTP features for instruments with usable history."""
        if window.max_age <= timedelta(0):
            raise ValueError("feature window max_age must be positive")

        snapshots: list[ScannerFeatureSnapshot] = []
        # DATA-012 defines an inclusive upper bound; the repository range is
        # half-open, so extend the end by one microsecond to include an event
        # exactly at reference_time.
        end_exclusive = window.end_time + timedelta(microseconds=1)

        for internal_id in universe.internal_ids:
            rows = self.reader.get_ltp(
                internal_id,
                window.start_time,
                end_exclusive,
            )
            if not rows:
                continue

            valid = [
                item
                for item in rows
                if item.internal_id == internal_id
                and item.event.segment == "CASH"
                and item.event.timestamp.tzinfo is not None
                and item.event.timestamp.utcoffset() is not None
                and window.contains(item.event.timestamp)
                and item.event.ltp > 0
            ]
            if not valid:
                continue

            prices = [item.event.ltp for item in valid]
            first = valid[0]
            latest = valid[-1]
            change_pct = ((latest.event.ltp - first.event.ltp) / first.event.ltp) * Decimal("100")
            snapshots.append(
                ScannerFeatureSnapshot(
                    internal_id=internal_id,
                    trading_symbol=latest.trading_symbol,
                    sample_count=len(valid),
                    first_ltp=first.event.ltp,
                    latest_ltp=latest.event.ltp,
                    high_ltp=max(prices),
                    low_ltp=min(prices),
                    change_pct=change_pct,
                )
            )

        return tuple(snapshots)
