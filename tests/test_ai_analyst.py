"""Deterministic tests for the AI-001 analyst boundary."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision, AIAnalysis, AIAnalysisContext, AIAnalyst


def context() -> AIAnalysisContext:
    return AIAnalysisContext(
        instrument="NSE:CASH:RELIANCE",
        timeframe="15m",
        market_features={"latest_ltp": Decimal("2500")},
        signal_features={"direction": "long", "score": Decimal("2.5")},
        relevant_context={"news": "none supplied"},
        portfolio_constraints={"max_risk_pct": Decimal("1")},
    )


class StubProvider:
    def __init__(self, result: AIAnalysis):
        self.result = result
        self.received: AIAnalysisContext | None = None

    def analyze(self, received: AIAnalysisContext) -> AIAnalysis:
        self.received = received
        return self.result


def result(**overrides: object) -> AIAnalysis:
    values: dict[str, object] = {
        "decision": AIDecision.BUY,
        "confidence": Decimal("0.82"),
        "setup": "momentum continuation",
        "reason_codes": ("MOMENTUM_POSITIVE",),
        "entry": Decimal("2500"),
        "stop_loss": Decimal("2475"),
        "target": Decimal("2550"),
        "invalidation": "signal loses positive momentum",
        "model_version": "test-model-1",
        "prompt_version": "ai-001-v1",
    }
    values.update(overrides)
    return AIAnalysis(**values)


def test_analyst_validates_context_and_provider_output() -> None:
    provider = StubProvider(result())

    analysis = AIAnalyst(provider).analyze(context())

    assert provider.received == context()
    assert analysis.decision is AIDecision.BUY
    assert analysis.confidence == Decimal("0.82")


def test_no_trade_is_a_valid_fail_closed_decision() -> None:
    provider = StubProvider(
        result(
            decision=AIDecision.NO_TRADE,
            confidence=Decimal("0.99"),
            setup="insufficient confirmation",
            reason_codes=("INSUFFICIENT_CONFIRMATION",),
            entry=None,
            stop_loss=None,
            target=None,
        )
    )

    analysis = AIAnalyst(provider).analyze(context())

    assert analysis.decision is AIDecision.NO_TRADE
    assert analysis.entry is None


def test_context_rejects_empty_instrument() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        AIAnalysisContext(
            instrument="  ",
            timeframe="15m",
            market_features={},
            signal_features={},
            relevant_context={},
            portfolio_constraints={},
        )


def test_analysis_rejects_out_of_range_confidence() -> None:
    with pytest.raises(ValueError, match="less than or equal to 1"):
        result(confidence=Decimal("1.01"))


def test_analysis_rejects_non_positive_prices() -> None:
    with pytest.raises(ValueError, match="prices must be positive"):
        result(entry=Decimal("0"))
