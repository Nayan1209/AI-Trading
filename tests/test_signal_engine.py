from decimal import Decimal

import pytest

from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.signal_engine import (
    SignalCandidate,
    SignalDirection,
    SignalEngine,
    SignalType,
)
from src.signal_strategies import BreakoutSignalStrategy, MomentumSignalStrategy, ReversalSignalStrategy


def candidate(rank: int, internal_id: str, symbol: str = "RELIANCE", change_pct: str = "5", *, latest_ltp: str = "105", high_ltp: str = "106", low_ltp: str = "99") -> ScannerRankedCandidate:
    snapshot = ScannerFeatureSnapshot(
        internal_id=internal_id,
        trading_symbol=symbol,
        sample_count=3,
        first_ltp=Decimal("100"),
        latest_ltp=Decimal(latest_ltp),
        high_ltp=Decimal(high_ltp),
        low_ltp=Decimal(low_ltp),
        change_pct=Decimal(change_pct),
    )
    return ScannerRankedCandidate(rank=rank, snapshot=snapshot)


def test_signal_engine_returns_no_signals_without_strategies() -> None:
    ranked = (candidate(1, "NSE:CASH:RELIANCE"),)

    assert SignalEngine().generate(ranked) == ()


def test_signal_engine_evaluates_strategies_in_deterministic_candidate_order() -> None:
    ranked = (
        candidate(1, "NSE:CASH:RELIANCE"),
        candidate(2, "NSE:CASH:INFY", symbol="INFY"),
    )

    result = SignalEngine((MomentumSignalStrategy(),)).generate(ranked)

    assert tuple(signal.internal_id for signal in result) == (
        "NSE:CASH:RELIANCE",
        "NSE:CASH:INFY",
    )
    assert all(signal.signal_type is SignalType.MOMENTUM for signal in result)


def test_signal_engine_momentum_factory_wires_concrete_strategy() -> None:
    ranked = (
        candidate(1, "NSE:CASH:RELIANCE", change_pct="2.5"),
        candidate(2, "NSE:CASH:INFY", symbol="INFY", change_pct="0.5"),
        candidate(3, "NSE:CASH:TCS", symbol="TCS", change_pct="-2"),
    )

    result = SignalEngine.with_momentum_strategy().generate(ranked)

    assert tuple((signal.trading_symbol, signal.direction) for signal in result) == (
        ("RELIANCE", SignalDirection.LONG),
        ("TCS", SignalDirection.SHORT),
    )


def test_signal_engine_reversal_factory_wires_concrete_strategy() -> None:
    ranked = (
        candidate(1, "NSE:CASH:RELIANCE", change_pct="3"),
        candidate(2, "NSE:CASH:INFY", symbol="INFY", change_pct="1.5"),
        candidate(3, "NSE:CASH:TCS", symbol="TCS", change_pct="-3"),
    )

    result = SignalEngine.with_reversal_strategy().generate(ranked)

    assert tuple((signal.trading_symbol, signal.direction) for signal in result) == (
        ("RELIANCE", SignalDirection.SHORT),
        ("TCS", SignalDirection.LONG),
    )


def test_signal_engine_breakout_factory_wires_concrete_strategy() -> None:
    ranked = (
        candidate(1, "NSE:CASH:RELIANCE", change_pct="2", latest_ltp="102", high_ltp="102"),
        candidate(2, "NSE:CASH:INFY", symbol="INFY", change_pct="2", latest_ltp="102", high_ltp="103"),
        candidate(3, "NSE:CASH:TCS", symbol="TCS", change_pct="-2", latest_ltp="98", low_ltp="98"),
    )

    result = SignalEngine.with_breakout_strategy().generate(ranked)

    assert tuple((signal.trading_symbol, signal.direction) for signal in result) == (
        ("RELIANCE", SignalDirection.LONG),
        ("TCS", SignalDirection.SHORT),
    )


def test_signal_engine_accepts_empty_shortlist() -> None:
    assert SignalEngine((MomentumSignalStrategy(),)).generate(()) == ()


def test_signal_engine_rejects_duplicate_strategy_types() -> None:
    with pytest.raises(ValueError, match="unique signal types"):
        SignalEngine((MomentumSignalStrategy(), MomentumSignalStrategy()))


def test_signal_candidate_rejects_out_of_range_score() -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        SignalCandidate(
            rank=1,
            internal_id="NSE:CASH:RELIANCE",
            trading_symbol="RELIANCE",
            signal_type=SignalType.MOMENTUM,
            direction=SignalDirection.LONG,
            strategy_score=Decimal("101"),
            reason_codes=("test",),
        )


def test_signal_engine_rejects_strategy_contract_mismatch() -> None:
    class BadStrategy:
        signal_type = SignalType.MOMENTUM

        def evaluate(self, candidate: ScannerRankedCandidate) -> SignalCandidate:
            return SignalCandidate(
                rank=candidate.rank + 1,
                internal_id=candidate.snapshot.internal_id,
                trading_symbol=candidate.snapshot.trading_symbol,
                signal_type=SignalType.MOMENTUM,
                direction=SignalDirection.LONG,
                strategy_score=Decimal("50"),
                reason_codes=("bad_fixture",),
            )

    with pytest.raises(ValueError, match="mismatched rank"):
        SignalEngine((BadStrategy(),)).generate((candidate(1, "NSE:CASH:RELIANCE"),))
