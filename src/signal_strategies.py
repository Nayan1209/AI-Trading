"""Deterministic concrete signal strategies for SIG-001."""

from decimal import Decimal

from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.signal_engine import SignalCandidate, SignalDirection, SignalType


class MomentumSignalStrategy:
    """Emit a momentum signal from DATA-016 descriptive price change."""

    signal_type = SignalType.MOMENTUM

    def __init__(self, threshold_pct: Decimal = Decimal("1")) -> None:
        if threshold_pct <= Decimal("0"):
            raise ValueError("momentum threshold_pct must be positive")
        self.threshold_pct = threshold_pct

    def evaluate(self, candidate: ScannerRankedCandidate) -> SignalCandidate | None:
        change_pct = candidate.snapshot.change_pct
        if abs(change_pct) <= self.threshold_pct:
            return None

        direction = SignalDirection.LONG if change_pct > 0 else SignalDirection.SHORT
        score = min(abs(change_pct), Decimal("100"))
        reason = (
            "change_pct_above_momentum_threshold"
            if direction is SignalDirection.LONG
            else "change_pct_below_momentum_threshold"
        )
        return SignalCandidate(
            rank=candidate.rank,
            internal_id=candidate.snapshot.internal_id,
            trading_symbol=candidate.snapshot.trading_symbol,
            signal_type=SignalType.MOMENTUM,
            direction=direction,
            strategy_score=score,
            reason_codes=(reason,),
        )
