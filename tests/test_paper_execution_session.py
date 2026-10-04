from decimal import Decimal

from src.ai_analyst import AIDecision
from src.paper_execution_session import PaperExecutionSession
from src.paper_order_ledger import PaperOrderLedger
from src.trade_planner import TradePlan


def plan() -> TradePlan:
    return TradePlan(
        decision=AIDecision.BUY,
        entry=Decimal("100"),
        stop_loss=Decimal("95"),
        target=Decimal("110"),
        quantity=10,
        risk_budget=Decimal("500"),
        estimated_risk=Decimal("50"),
        notional_value=Decimal("1000"),
        reason="test plan",
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
    )


def test_session_executes_records_and_reconciles() -> None:
    session = PaperExecutionSession()

    result = session.execute(plan(), fill_price=Decimal("101"))

    assert result.order.status.value == "FILLED"
    assert result.order.quantity == 10
    assert result.reconciliation.matched is True
    assert result.reconciliation.expected_count == 1
    assert result.reconciliation.recorded_count == 1
    assert session.ledger.snapshot() == (result.order,)


def test_session_preserves_existing_ledger_history() -> None:
    ledger = PaperOrderLedger()
    first = PaperExecutionSession(ledger=ledger).execute(
        plan(), fill_price=Decimal("101")
    ).order

    session = PaperExecutionSession(ledger=ledger)
    result = session.execute(plan(), fill_price=Decimal("102"))

    assert result.reconciliation.matched is True
    assert result.reconciliation.expected_count == 2
    assert result.reconciliation.recorded_count == 2
    assert ledger.snapshot() == (first, result.order)


def test_session_result_is_immutable() -> None:
    result = PaperExecutionSession().execute(plan(), fill_price=Decimal("101"))

    try:
        result.order = result.order
    except AttributeError:
        pass
    else:
        raise AssertionError("session result must be immutable")


def test_session_rejects_non_positive_fill_price() -> None:
    session = PaperExecutionSession()

    try:
        session.execute(plan(), fill_price=Decimal("0"))
    except ValueError as exc:
        assert str(exc) == "paper fill price must be positive"
    else:
        raise AssertionError("non-positive fill price must be rejected")
