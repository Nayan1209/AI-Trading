from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperExecutionEngine, PaperOrderStatus
from src.trade_planner import TradePlan


def plan(decision: AIDecision = AIDecision.BUY, quantity: int = 10) -> TradePlan:
    return TradePlan(
        decision=decision,
        entry=Decimal("100"),
        stop_loss=Decimal("95") if decision is AIDecision.BUY else Decimal("105"),
        target=Decimal("110") if decision is AIDecision.BUY else Decimal("90"),
        quantity=quantity,
        risk_budget=Decimal("500"),
        estimated_risk=Decimal("50"),
        notional_value=Decimal("1000"),
        reason="test plan",
    )


def test_buy_plan_produces_deterministic_filled_paper_order() -> None:
    engine = PaperExecutionEngine()

    first = engine.execute(plan(), fill_price=Decimal("101"))
    second = engine.execute(plan(), fill_price=Decimal("101"))

    assert first == second
    assert first.order_id.startswith("PAPER-")
    assert first.decision is AIDecision.BUY
    assert first.quantity == 10
    assert first.fill_price == Decimal("101")
    assert first.status is PaperOrderStatus.FILLED


def test_sell_plan_preserves_side_and_quantity() -> None:
    result = PaperExecutionEngine().execute(
        plan(AIDecision.SELL, quantity=25),
        fill_price=Decimal("99"),
    )

    assert result.decision is AIDecision.SELL
    assert result.quantity == 25
    assert result.fill_price == Decimal("99")


def test_non_paper_environment_is_rejected() -> None:
    with pytest.raises(ValueError, match="environment='paper'"):
        PaperExecutionEngine().execute(plan(), fill_price=Decimal("100"), environment="production")


def test_non_positive_quantity_is_rejected() -> None:
    with pytest.raises(ValueError, match="quantity must be positive"):
        PaperExecutionEngine().execute(plan(quantity=0), fill_price=Decimal("100"))


def test_non_positive_fill_price_is_rejected() -> None:
    with pytest.raises(ValueError, match="fill price must be positive"):
        PaperExecutionEngine().execute(plan(), fill_price=Decimal("0"))


def test_non_trade_decision_is_rejected() -> None:
    with pytest.raises(ValueError, match="requires BUY or SELL"):
        PaperExecutionEngine().execute(plan(AIDecision.WATCH), fill_price=Decimal("100"))


def test_invalid_plan_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="TradePlan"):
        PaperExecutionEngine().execute(object(), fill_price=Decimal("100"))
