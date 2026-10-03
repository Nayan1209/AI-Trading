"""Deterministic tests for RISK-001."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision, AIAnalysis
from src.risk_engine import RiskEngine


def analysis(decision: AIDecision = AIDecision.BUY) -> AIAnalysis:
    return AIAnalysis(
        decision=decision,
        confidence=Decimal("0.9"),
        setup="test setup",
        reason_codes=("TEST",),
        entry=Decimal("100"),
        stop_loss=Decimal("95") if decision is AIDecision.BUY else Decimal("105"),
        target=Decimal("110") if decision is AIDecision.BUY else Decimal("90"),
        invalidation="stop hit",
        model_version="test-model",
        prompt_version="test-prompt",
    )


def test_buy_quantity_is_bounded_by_risk_and_lot_size() -> None:
    result = RiskEngine().evaluate(
        analysis(),
        equity=Decimal("100000"),
        risk_pct=Decimal("1"),
        max_notional_pct=Decimal("20"),
        lot_size=10,
    )

    assert result.approved is True
    assert result.quantity == 200
    assert result.estimated_risk == Decimal("1000")
    assert result.notional_value == Decimal("20000")


def test_sell_uses_same_absolute_stop_distance() -> None:
    result = RiskEngine().evaluate(
        analysis(AIDecision.SELL),
        equity=Decimal("100000"),
        risk_pct=Decimal("0.5"),
        max_notional_pct=Decimal("20"),
        lot_size=25,
    )

    assert result.quantity == 100
    assert result.estimated_risk == Decimal("500")


def test_watch_is_rejected() -> None:
    advisory = analysis(AIDecision.WATCH).model_copy(
        update={"entry": None, "stop_loss": None, "target": None}
    )
    with pytest.raises(ValueError, match="requires BUY or SELL"):
        RiskEngine().evaluate(
            advisory,
            equity=Decimal("100000"),
            risk_pct=Decimal("1"),
            max_notional_pct=Decimal("20"),
        )


def test_zero_quantity_is_rejected() -> None:
    with pytest.raises(ValueError, match="zero executable quantity"):
        RiskEngine().evaluate(
            analysis(),
            equity=Decimal("1000"),
            risk_pct=Decimal("0.1"),
            max_notional_pct=Decimal("1"),
            lot_size=100,
        )


def test_invalid_risk_limits_are_rejected() -> None:
    with pytest.raises(ValueError, match="risk_pct"):
        RiskEngine().evaluate(
            analysis(),
            equity=Decimal("100000"),
            risk_pct=Decimal("0"),
            max_notional_pct=Decimal("20"),
        )


def test_quantity_never_exceeds_notional_cap() -> None:
    result = RiskEngine().evaluate(
        analysis(),
        equity=Decimal("100000"),
        risk_pct=Decimal("10"),
        max_notional_pct=Decimal("5"),
        lot_size=1,
    )

    assert result.notional_value <= Decimal("5000")
    assert result.estimated_risk <= Decimal("10000")
