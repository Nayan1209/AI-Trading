from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperExecutionEngine, PaperOrderStatus
from src.trade_planner import TradePlan


def plan(
    decision: AIDecision = AIDecision.BUY,
    quantity: int = 10,
    *,
    internal_id: str = "NSE:CASH:RELIANCE",
    trading_symbol: str = "RELIANCE",
    client_order_id: str = "CLIENT-TEST-001",
) -> TradePlan:
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
        internal_id=internal_id,
        trading_symbol=trading_symbol,
        client_order_id=client_order_id,
    )


def test_buy_plan_produces_repeatable_order_identity() -> None:
    engine = PaperExecutionEngine()
    trade_plan = plan()

    first = engine.execute(trade_plan, fill_price=Decimal("101"))
    second = engine.execute(trade_plan, fill_price=Decimal("101"))

    assert first.order_id == second.order_id
    assert first.created_at != second.created_at
    assert first.order_id.startswith("PAPER-")
    assert first.internal_id == "NSE:CASH:RELIANCE"
    assert first.trading_symbol == "RELIANCE"
    assert first.client_order_id == "CLIENT-TEST-001"
    assert first.decision is AIDecision.BUY
    assert first.quantity == 10
    assert first.fill_price == Decimal("101")
    assert first.status is PaperOrderStatus.FILLED


def test_identical_trade_values_for_different_symbols_produce_different_order_ids() -> None:
    engine = PaperExecutionEngine()

    reliance = engine.execute(plan(), fill_price=Decimal("101"))
    tcs = engine.execute(
        plan(internal_id="NSE:CASH:TCS", trading_symbol="TCS"),
        fill_price=Decimal("101"),
    )

    assert reliance.order_id != tcs.order_id


def test_new_client_order_id_allows_intentional_repeat_trade() -> None:
    engine = PaperExecutionEngine()

    first = engine.execute(plan(client_order_id="CLIENT-001"), fill_price=Decimal("101"))
    second = engine.execute(plan(client_order_id="CLIENT-002"), fill_price=Decimal("101"))

    assert first.order_id != second.order_id
    assert first.client_order_id != second.client_order_id


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


def test_missing_instrument_identity_is_rejected() -> None:
    with pytest.raises(ValueError, match="internal_id"):
        PaperExecutionEngine().execute(
            plan(internal_id=""),
            fill_price=Decimal("100"),
        )
