"""Deterministic tests for the AI-003 analysis orchestration boundary."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision, AIAnalysis, AIAnalysisContext, AIAnalyst
from src.ai_context import AIAnalysisContextBuilder
from src.ai_service import AIAnalysisService
from src.signal_engine import SignalCandidate, SignalDirection, SignalType


def signal() -> SignalCandidate:
    return SignalCandidate(
        rank=1,
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
        signal_type=SignalType.BREAKOUT,
        direction=SignalDirection.LONG,
        strategy_score=Decimal("4.2"),
        reason_codes=("BREAKOUT_CONFIRMATION",),
    )


def analysis() -> AIAnalysis:
    return AIAnalysis(
        decision=AIDecision.BUY,
        confidence=Decimal("0.84"),
        setup="breakout continuation",
        reason_codes=("BREAKOUT_CONFIRMATION",),
        entry=Decimal("2500"),
        stop_loss=Decimal("2475"),
        target=Decimal("2550"),
        invalidation="latest price loses breakout confirmation",
        model_version="stub-model-1",
        prompt_version="ai-003-v1",
    )


class StubProvider:
    def __init__(self) -> None:
        self.received: AIAnalysisContext | None = None

    def analyze(self, context: AIAnalysisContext) -> AIAnalysis:
        self.received = context
        return analysis()


def test_service_composes_context_builder_and_analyst() -> None:
    provider = StubProvider()
    service = AIAnalysisService(AIAnalyst(provider))

    result = service.analyze_signal(
        signal(),
        timeframe="15m",
        market_features={"latest_ltp": Decimal("2500")},
        relevant_context={"news": "none supplied"},
        portfolio_constraints={"max_risk_pct": Decimal("1")},
    )

    assert provider.received is not None
    assert provider.received.instrument == "NSE:CASH:RELIANCE"
    assert provider.received.timeframe == "15m"
    assert provider.received.signal_features["rank"] == 1
    assert provider.received.signal_features["signal_type"] == "breakout"
    assert provider.received.signal_features["direction"] == "long"
    assert result.decision is AIDecision.BUY
    assert result.confidence == Decimal("0.84")


def test_service_preserves_caller_supplied_context() -> None:
    provider = StubProvider()
    service = AIAnalysisService(AIAnalyst(provider))
    market = {"latest_ltp": Decimal("2500")}
    relevant = {"news": "none supplied"}
    constraints = {"max_risk_pct": Decimal("1")}

    service.analyze_signal(
        signal(),
        timeframe="15m",
        market_features=market,
        relevant_context=relevant,
        portfolio_constraints=constraints,
    )

    assert provider.received is not None
    assert provider.received.market_features == market
    assert provider.received.relevant_context == relevant
    assert provider.received.portfolio_constraints == constraints


def test_service_reuses_ai_002_timeframe_validation() -> None:
    provider = StubProvider()
    service = AIAnalysisService(
        AIAnalyst(provider),
        context_builder=AIAnalysisContextBuilder(),
    )

    with pytest.raises(ValueError, match="must not be empty"):
        service.analyze_signal(
            signal(),
            timeframe=" ",
            market_features={},
            relevant_context={},
            portfolio_constraints={},
        )


def test_service_returns_fail_closed_no_trade_result() -> None:
    class NoTradeProvider(StubProvider):
        def analyze(self, context: AIAnalysisContext) -> AIAnalysis:
            self.received = context
            return AIAnalysis(
                decision=AIDecision.NO_TRADE,
                confidence=Decimal("0.99"),
                setup="insufficient confirmation",
                reason_codes=("INSUFFICIENT_CONFIRMATION",),
                invalidation="no confirmed setup",
                model_version="stub-model-1",
                prompt_version="ai-003-v1",
            )

    result = AIAnalysisService(AIAnalyst(NoTradeProvider())).analyze_signal(
        signal(),
        timeframe="15m",
        market_features={},
        relevant_context={},
        portfolio_constraints={},
    )

    assert result.decision is AIDecision.NO_TRADE
    assert result.entry is None
    assert result.stop_loss is None
    assert result.target is None
