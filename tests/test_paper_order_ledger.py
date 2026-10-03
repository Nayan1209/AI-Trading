from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperExecutionEngine, PaperOrder
from src.paper_order_ledger import PaperOrderLedger
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


def order(decision: AIDecision = AIDecision.BUY, quantity: int = 10) -> PaperOrder:
    return PaperOrderLedgerOrderFactory.create(decision, quantity)


class PaperOrderLedgerOrderFactory:
    @staticmethod
    def create(decision: AIDecision, quantity: int) -> PaperOrder:
        return PaperExecutionEngine().execute(
            plan(decision, quantity),
            fill_price=Decimal("101") if decision is AIDecision.BUY else Decimal("99"),
        )


def test_record_preserves_immutable_order_and_insertion_order() -> None:
    ledger = PaperOrderLedger()
    first = order(AIDecision.BUY, 10)
    second = order(AIDecision.SELL, 25)

    assert ledger.record(first) == first
    assert ledger.record(second) == second
    assert ledger.snapshot() == (first, second)
    assert ledger.get(first.order_id) == first
    assert ledger.get(second.order_id) == second


def test_duplicate_order_id_is_rejected() -> None:
    ledger = PaperOrderLedger()
    first = order()
    ledger.record(first)

    with pytest.raises(ValueError, match="already recorded"):
        ledger.record(first)


def test_missing_order_id_is_rejected() -> None:
    with pytest.raises(KeyError):
        PaperOrderLedger().get("PAPER-missing")


def test_non_paper_order_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="PaperOrder"):
        PaperOrderLedger().record(object())


def test_empty_snapshot_is_immutable_tuple() -> None:
    snapshot = PaperOrderLedger().snapshot()

    assert snapshot == ()
    assert isinstance(snapshot, tuple)
