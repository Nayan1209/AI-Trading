from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Sequence

from .models import Candle
from .validation import validate_candle


@dataclass(frozen=True)
class DataQualityReport:
    """Deterministic quality result for a normalized candle batch."""

    total_candles: int
    unique_candles: int
    duplicate_count: int
    invalid_count: int
    missing_timestamps: tuple[datetime, ...]
    completeness_ratio: float
    errors: tuple[str, ...]
    persistence_healthy: bool | None = None
    persistence_error: str | None = None

    @property
    def gap_count(self) -> int:
        return len(self.missing_timestamps)

    @property
    def healthy(self) -> bool:
        return (
            self.invalid_count == 0
            and self.duplicate_count == 0
            and self.gap_count == 0
            and (self.persistence_healthy is not False)
        )


def assess_candles(
    candles: Sequence[Candle],
    expected_timestamps: Sequence[datetime] = (),
) -> DataQualityReport:
    """Assess completeness, duplicates and candle validity without external services.

    ``expected_timestamps`` is caller-supplied deliberately: market sessions contain
    legitimate overnight/weekend gaps, so the monitor must not invent a trading
    calendar. Missing expected timestamps are reported as gaps.
    """
    seen: set[tuple[str, str, str, datetime]] = set()
    duplicate_count = 0
    invalid_count = 0
    errors: list[str] = []

    for index, candle in enumerate(candles):
        identity = (candle.symbol, candle.exchange, candle.timeframe, candle.timestamp)
        if identity in seen:
            duplicate_count += 1
        else:
            seen.add(identity)

        try:
            validate_candle(candle)
        except ValueError as exc:
            invalid_count += 1
            errors.append(f"candle[{index}]: {exc}")

    expected = set(expected_timestamps)
    for timestamp in expected:
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("expected timestamps must be timezone-aware")

    observed_timestamps = {candle.timestamp for candle in candles}
    missing = tuple(sorted(expected - observed_timestamps))
    completeness_ratio = (
        len(expected - set(missing)) / len(expected) if expected else 1.0
    )

    if duplicate_count:
        errors.append(f"duplicate candles detected: {duplicate_count}")
    if missing:
        errors.append(f"missing expected candles: {len(missing)}")

    return DataQualityReport(
        total_candles=len(candles),
        unique_candles=len(seen),
        duplicate_count=duplicate_count,
        invalid_count=invalid_count,
        missing_timestamps=missing,
        completeness_ratio=completeness_ratio,
        errors=tuple(errors),
    )


def assess_persistence_health(check: Callable[[], bool]) -> tuple[bool, str | None]:
    """Run a caller-supplied persistence health check without hiding failures."""
    try:
        healthy = check()
    except Exception as exc:  # pragma: no cover - exact database exception is caller-defined
        return False, f"persistence health check failed: {exc}"
    if not healthy:
        return False, "persistence health check returned unhealthy"
    return True, None
