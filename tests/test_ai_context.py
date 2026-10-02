"""Deterministic tests for the AI-002 context builder."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIAnalysisContext
from src.ai_context import AIAnalysisContextBuilder
from src.signal_engine import SignalCandidate, SignalDirection, SignalType


def signal() -> SignalCandidate:
    return SignalCandidate(
        rank=2,
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
        signal_type=SignalType.MOMENTUM,
        direction=SignalDirection.LONG,
        strategy_score=Decimal("82.5"),
        reason_codes=("MOMENTUM_POSITIVE", "BREAKOUT_CONFIRMATION"),
    )


def test_builder_maps_signal_to_ai_context() -> None:
    context = AIAnalysisContextBuilder().build(
        signal(),
        timeframe="15m",
        market_features={"latest_ltp": Decimal("2500")},
        relevant_context={"news": "none supplied"},
        portfolio_constraints={"max_risk_pct": Decimal("1")},
    )

    assert isinstance(context, AIAnalysisContext)
    assert context.instrument == "NSE:CASH:RELIANCE"
    assert context.timeframe == "15m"
    assert context.signal_features == {
        "rank": 2,
        "trading_symbol": "RELIANCE",
        "signal_type": "momentum",
        "direction": "long",
        "strategy_score": Decimal("82.5"),
        "reason_codes": ("MOMENTUM_POSITIVE", "BREAKOUT_CONFIRMATION"),
    }


def test_builder_preserves_caller_supplied_context_without_inventing_values() -> None:
    market = {"latest_ltp": Decimal("2500")}
    relevant = {"news": "none supplied"}
    constraints = {"max_risk_pct": Decimal("1")}

    context = AIAnalysisContextBuilder().build(
        signal(),
        timeframe="15m",
        market_features=market,
        relevant_context=relevant,
        portfolio_constraints=constraints,
    )

    assert context.market_features == market
    assert context.relevant_context == relevant
    assert context.portfolio_constraints == constraints


def test_builder_rejects_empty_timeframe() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        AIAnalysisContextBuilder().build(
            signal(),
            timeframe="  ",
            market_features={},
            relevant_context={},
            portfolio_constraints={},
        )


def test_builder_preserves_neutral_signal_as_data() -> None:
    neutral = SignalCandidate(
        rank=1,
        internal_id="NSE:CASH:TCS",
        trading_symbol="TCS",
        signal_type=SignalType.MOMENTUM,
        direction=SignalDirection.NEUTRAL,
        strategy_score=Decimal("0"),
        reason_codes=("NO_DIRECTIONAL_EDGE",),
    )

    context = AIAnalysisContextBuilder().build(
        neutral,
        timeframe="15m",
        market_features={},
        relevant_context={},
        portfolio_constraints={},
    )

    assert context.signal_features["direction"] == "neutral"
    assert context.signal_features["strategy_score"] == Decimal("0")
