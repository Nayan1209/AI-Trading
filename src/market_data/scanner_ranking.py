"""Deterministic ordering of validated scanner feature snapshots."""

from dataclasses import dataclass

from src.market_data.scanner_feature_quality import ScannerFeatureQualityGate
from src.market_data.scanner_features import ScannerFeatureSnapshot


@dataclass(frozen=True)
class ScannerRankedCandidate:
    """A validated scanner snapshot with its deterministic rank."""

    rank: int
    snapshot: ScannerFeatureSnapshot


class ScannerRankingService:
    """Rank validated scanner candidates without generating trading signals."""

    def __init__(self, min_samples: int = 1):
        self.quality_gate = ScannerFeatureQualityGate(min_samples=min_samples)

    def rank(
        self,
        snapshots: tuple[ScannerFeatureSnapshot, ...] | list[ScannerFeatureSnapshot],
    ) -> tuple[ScannerRankedCandidate, ...]:
        """Validate and deterministically rank scanner feature snapshots.

        Ordering is strongest descriptive percentage change first, then higher
        sample count, then lexical internal ID. No score, signal, or execution
        decision is created here.
        """
        validated = self.quality_gate.validate(snapshots)
        ordered = sorted(
            validated,
            key=lambda item: (-item.change_pct, -item.sample_count, item.internal_id),
        )
        return tuple(
            ScannerRankedCandidate(rank=index, snapshot=snapshot)
            for index, snapshot in enumerate(ordered, start=1)
        )
