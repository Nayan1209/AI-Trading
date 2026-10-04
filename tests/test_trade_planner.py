"""Deterministic tests for PLAN-001."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision, AIAnalysis
from src.trade_planner import TradePlanner


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


def plan_kwargs() -> dict[str, str]:
    return {"internal_id": "NSE:CASH:RELIANCE", "trading_symbol": "RELIANCE"}


def test_buy_plan_is_bounded_by_risk_gate() -> None:
    plan = TradePlanner().plan(
        analysis(),
        equity=Decimal("100000"),
        risk_pct=Decimal("1"),
        max_notional_pct=Decimal("20"),
        lot_size=10,
        **plan_kwargs(),
    )

    assert plan.decision is AIDecision.BUY
    assert plan.internal_id == "NSE:CASH:RELIANCE"
    assert plan.trading_symbol == "RELIANCE"
    assert plan.client_order_id.startswith("CLIENT-")
    assert plan.entry == Decimal("100")
    assert plan.stop_loss == Decimal("95")
    assert plan.target == Decimal("110")
    assert plan.quantity == 200
    assert plan.estimated_risk == Decimal("1000")
    assert plan.notional_value == Decimal("20000")


def test_sell_plan_preserves_sell_price_semantics() -> None:
    plan = TradePlanner().plan(
        analysis(AIDecision.SELL),
        equity=Decimal("100000"),
        risk_pct=Decimal("0.5"),
        max_notional_pct=Decimal("20"),
        lot_size=25,
        **plan_kwargs(),
    )

    assert plan.decision is AIDecision.SELL
    assert plan.target < plan.entry < plan.stop_loss
    assert plan.quantity == 100
    assert plan.estimated_risk == Decimal("500")


def test_watch_cannot_become_trade_plan() -> None:
    advisory = analysis(AIDecision.WATCH).model_copy(
        update={"entry": None, "stop_loss": None, "target": None}
    )

    with pytest.raises(ValueError, match="requires BUY or SELL"):
        TradePlanner().plan(
            advisory,
            equity=Decimal("100000"),
            risk_pct=Decimal("1"),
            max_notional_pct=Decimal("20"),
            **plan_kwargs(),
        )


def test_invalid_risk_limit_is_rejected_before_plan() -> None:
    with pytest.raises(ValueError, match="risk_pct"):
        TradePlanner().plan(
            analysis(),
            equity=Decimal("100000"),
            risk_pct=Decimal("0"),
            max_notional_pct=Decimal("20"),
            **plan_kwargs(),
        )


def test_missing_instrument_identity_is_rejected() -> None:
    with pytest.raises(ValueError, match="internal_id"):
        TradePlanner().plan(
            analysis(),
            equity=Decimal("100000"),
            risk_pct=Decimal("1"),
            max_notional_pct=Decimal("20"),
            internal_id="",
            trading_symbol="RELIANCE",
        )


def test_plan_is_immutable() -> None:
    plan = TradePlanner().plan(
        analysis(),
        equity=Decimal("100000"),
        risk_pct=Decimal("1"),
        max_notional_pct=Decimal("20"),
        **plan_kwargs(),
    )

    with pytest.raises((AttributeError, TypeError)):
        plan.quantity = 1  # type: ignore[misc]
