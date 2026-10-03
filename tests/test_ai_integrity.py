"""Deterministic tests for the AI-007 analysis integrity gate."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision, AIAnalysis
from src.ai_integrity import AIAnalysisIntegrityGate


def analysis(
    decision: AIDecision = AIDecision.BUY,
    entry: str | None = "100",
    stop_loss: str | None = "98",
    target: str | None = "104",
) -> AIAnalysis:
    return AIAnalysis(
        decision=decision,
        confidence=Decimal("0.82"),
        setup="momentum continuation",
        reason_codes=("MOMENTUM",),
        entry=Decimal(entry) if entry is not None else None,
        stop_loss=Decimal(stop_loss) if stop_loss is not None else None,
        target=Decimal(target) if target is not None else None,
        invalidation="breaks support",
        model_version="fake-model-v1",
        prompt_version="ai-004-v1",
    )


def test_valid_buy_is_accepted() -> None:
    result = AIAnalysisIntegrityGate.validate(analysis())
    assert result is not None
    assert result.decision is AIDecision.BUY


def test_valid_sell_is_accepted() -> None:
    result = AIAnalysisIntegrityGate.validate(
        analysis(AIDecision.SELL, entry="100", stop_loss="104", target="96")
    )
    assert result.decision is AIDecision.SELL


def test_directional_trade_requires_all_prices() -> None:
    with pytest.raises(ValueError, match="requires entry, stop_loss, and target"):
        AIAnalysisIntegrityGate.validate(analysis(entry="100", stop_loss=None, target="104"))


def test_buy_price_order_is_enforced() -> None:
    with pytest.raises(ValueError, match="BUY analysis requires stop_loss < entry < target"):
        AIAnalysisIntegrityGate.validate(analysis(entry="100", stop_loss="101", target="104"))


def test_sell_price_order_is_enforced() -> None:
    with pytest.raises(ValueError, match="SELL analysis requires target < entry < stop_loss"):
        AIAnalysisIntegrityGate.validate(
            analysis(AIDecision.SELL, entry="100", stop_loss="99", target="96")
        )


def test_watch_without_prices_is_accepted() -> None:
    result = AIAnalysisIntegrityGate.validate(
        analysis(AIDecision.WATCH, entry=None, stop_loss=None, target=None)
    )
    assert result.decision is AIDecision.WATCH


def test_no_trade_without_prices_is_accepted() -> None:
    result = AIAnalysisIntegrityGate.validate(
        analysis(AIDecision.NO_TRADE, entry=None, stop_loss=None, target=None)
    )
    assert result.decision is AIDecision.NO_TRADE


def test_advisory_decisions_cannot_carry_execution_prices() -> None:
    with pytest.raises(ValueError, match="WATCH/NO_TRADE analysis must not contain execution prices"):
        AIAnalysisIntegrityGate.validate(
            analysis(AIDecision.WATCH, entry="100", stop_loss=None, target=None)
        )


def test_gate_preserves_the_immutable_analysis() -> None:
    original = analysis()
    assert AIAnalysisIntegrityGate.validate(original) is original
