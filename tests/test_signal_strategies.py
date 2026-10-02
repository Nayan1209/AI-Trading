from decimal import Decimal

import pytest

from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.signal_engine import SignalDirection, SignalType
from src.signal_strategies import MomentumSignalStrategy, ReversalSignalStrategy


def candidate(change_pct: str) -> ScannerRankedCandidate:
    return ScannerRankedCandidate(
        rank=1,
        snapshot=ScannerFeatureSnapshot(
            internal_id="NSE:CASH:RELIANCE",
            trading_symbol="RELIANCE",
            sample_count=3,
            first_ltp=Decimal("100"),
            latest_ltp=Decimal("105"),
            high_ltp=Decimal("106"),
            low_ltp=Decimal("99"),
            change_pct=Decimal(change_pct),
        ),
    )


def test_momentum_emits_long_above_threshold() -> None:
    signal = MomentumSignalStrategy().evaluate(candidate("2.5"))
    assert signal is not None
    assert signal.signal_type is SignalType.MOMENTUM
    assert signal.direction is SignalDirection.LONG
    assert signal.strategy_score == Decimal("2.5")
    assert signal.reason_codes == ("change_pct_above_momentum_threshold",)


def test_momentum_emits_short_below_negative_threshold() -> None:
    signal = MomentumSignalStrategy().evaluate(candidate("-2.5"))
    assert signal is not None
    assert signal.direction is SignalDirection.SHORT
    assert signal.strategy_score == Decimal("2.5")
    assert signal.reason_codes == ("change_pct_below_momentum_threshold",)


def test_momentum_ignores_change_at_or_within_threshold() -> None:
    strategy = MomentumSignalStrategy()
    assert strategy.evaluate(candidate("1")) is None
    assert strategy.evaluate(candidate("-1")) is None
    assert strategy.evaluate(candidate("0.25")) is None


def test_momentum_caps_strategy_score_at_100() -> None:
    signal = MomentumSignalStrategy().evaluate(candidate("150"))
    assert signal is not None
    assert signal.strategy_score == Decimal("100")


def test_momentum_rejects_non_positive_threshold() -> None:
    with pytest.raises(ValueError, match="threshold_pct must be positive"):
        MomentumSignalStrategy(Decimal("0"))


def test_reversal_emits_short_on_positive_change_above_threshold() -> None:
    signal = ReversalSignalStrategy().evaluate(candidate("3"))
    assert signal is not None
    assert signal.signal_type is SignalType.REVERSAL
    assert signal.direction is SignalDirection.SHORT
    assert signal.strategy_score == Decimal("3")
    assert signal.reason_codes == ("change_pct_above_reversal_threshold",)


def test_reversal_emits_long_on_negative_change_below_threshold() -> None:
    signal = ReversalSignalStrategy().evaluate(candidate("-3"))
    assert signal is not None
    assert signal.direction is SignalDirection.LONG
    assert signal.strategy_score == Decimal("3")
    assert signal.reason_codes == ("change_pct_below_reversal_threshold",)


def test_reversal_ignores_change_at_or_within_threshold() -> None:
    strategy = ReversalSignalStrategy()
    assert strategy.evaluate(candidate("2")) is None
    assert strategy.evaluate(candidate("-2")) is None
    assert strategy.evaluate(candidate("1.5")) is None


def test_reversal_caps_strategy_score_at_100() -> None:
    signal = ReversalSignalStrategy().evaluate(candidate("150"))
    assert signal is not None
    assert signal.strategy_score == Decimal("100")


def test_reversal_rejects_non_positive_threshold() -> None:
    with pytest.raises(ValueError, match="threshold_pct must be positive"):
        ReversalSignalStrategy(Decimal("0"))
