"""Fail-closed validation for scanner feature snapshots."""

from decimal import Decimal

from src.market_data.scanner_features import ScannerFeatureSnapshot


class ScannerFeatureQualityGate:
    """Validate scanner features before downstream scanner consumption."""

    def __init__(self, min_samples: int = 1):
        if min_samples < 1:
            raise ValueError("min_samples must be positive")
        self.min_samples = min_samples

    def validate(
        self, snapshots: tuple[ScannerFeatureSnapshot, ...] | list[ScannerFeatureSnapshot]
    ) -> tuple[ScannerFeatureSnapshot, ...]:
        """Return deterministically ordered snapshots or fail closed."""
        seen: set[str] = set()
        accepted: list[ScannerFeatureSnapshot] = []

        for snapshot in snapshots:
            if not snapshot.internal_id.strip() or not snapshot.trading_symbol.strip():
                raise ValueError("scanner feature identity must be non-empty")
            if snapshot.internal_id in seen:
                raise ValueError("scanner feature snapshots contain duplicate internal_id")
            seen.add(snapshot.internal_id)
            if snapshot.sample_count < self.min_samples:
                raise ValueError("scanner feature sample_count is below minimum")

            prices = (
                snapshot.first_ltp,
                snapshot.latest_ltp,
                snapshot.high_ltp,
                snapshot.low_ltp,
            )
            if any(price <= Decimal("0") for price in prices):
                raise ValueError("scanner feature prices must be positive")
            if snapshot.high_ltp < snapshot.low_ltp:
                raise ValueError(
                    "scanner feature high_ltp must be greater than or equal to low_ltp"
                )

            expected_change = (
                (snapshot.latest_ltp - snapshot.first_ltp)
                / snapshot.first_ltp
                * Decimal("100")
            )
            if snapshot.change_pct != expected_change:
                raise ValueError(
                    "scanner feature change_pct is inconsistent with first/latest LTP"
                )

            accepted.append(snapshot)

        return tuple(sorted(accepted, key=lambda item: item.internal_id))
