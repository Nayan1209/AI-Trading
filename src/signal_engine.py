"""Deterministic signal-engine foundation for shortlisted scanner candidates."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Protocol, Sequence

from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.market_data.scanner_shortlist import ScannerCandidateShortlistService


class SignalType(StrEnum):
    """Supported strategy families reserved by the signal-engine contract."""

    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    MOMENTUM = "momentum"
    TREND_CONTINUATION = "trend_continuation"
    REVERSAL = "reversal"


class SignalDirection(StrEnum):
    """Directional bias emitted by a concrete strategy."""

    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class SignalCandidate:
    """A deterministic strategy observation passed to later AI/risk stages."""

    rank: int
    internal_id: str
    trading_symbol: str
    signal_type: SignalType
    direction: SignalDirection
    strategy_score: Decimal
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.rank <= 0:
            raise ValueError("rank must be positive")
        if not self.internal_id:
            raise ValueError("internal_id must not be empty")
        if not self.trading_symbol:
            raise ValueError("trading_symbol must not be empty")
        if not Decimal("0") <= self.strategy_score <= Decimal("100"):
            raise ValueError("strategy_score must be between 0 and 100")
        if not self.reason_codes:
            raise ValueError("reason_codes must not be empty")


class SignalStrategy(Protocol):
    """Strategy contract used by the signal engine."""

    signal_type: SignalType

    def evaluate(self, candidate: ScannerRankedCandidate) -> SignalCandidate | None:
        """Return a signal observation or ``None`` when the setup is absent."""
        ...


class SignalEngine:
    """Run deterministic signal strategies over a DATA-016 shortlist.

    SIG-001 deliberately provides the orchestration and contract boundary first.
    Concrete strategy rules are supplied independently and must not perform AI
    calls, risk overrides, broker operations, or order execution.
    """

    def __init__(self, strategies: Sequence[SignalStrategy] = ()):
        self._strategies = tuple(strategies)
        signal_types = [strategy.signal_type for strategy in self._strategies]
        if len(signal_types) != len(set(signal_types)):
            raise ValueError("signal strategies must have unique signal types")

    @classmethod
    def with_momentum_strategy(cls) -> "SignalEngine":
        """Build SIG-001 with the first concrete deterministic strategy."""
        from src.signal_strategies import MomentumSignalStrategy

        return cls((MomentumSignalStrategy(),))

    def generate(
        self,
        shortlist: tuple[ScannerRankedCandidate, ...] | list[ScannerRankedCandidate],
    ) -> tuple[SignalCandidate, ...]:
        """Evaluate each strategy against the existing deterministic shortlist."""
        candidates = tuple(shortlist)
        if not candidates:
            return ()

        ScannerCandidateShortlistService().shortlist(candidates, limit=len(candidates))

        signals: list[SignalCandidate] = []
        for candidate in candidates:
            for strategy in self._strategies:
                signal = strategy.evaluate(candidate)
                if signal is None:
                    continue
                if signal.rank != candidate.rank:
                    raise ValueError("strategy returned a mismatched rank")
                if signal.internal_id != candidate.snapshot.internal_id:
                    raise ValueError("strategy returned a mismatched internal_id")
                if signal.trading_symbol != candidate.snapshot.trading_symbol:
                    raise ValueError("strategy returned a mismatched trading_symbol")
                if signal.signal_type != strategy.signal_type:
                    raise ValueError("strategy returned a mismatched signal_type")
                signals.append(signal)

        return tuple(signals)
