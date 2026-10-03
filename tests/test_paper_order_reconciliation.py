"""Tests for the deterministic PAPER-003 reconciliation boundary."""

from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperOrder, PaperOrderStatus
from src.paper_order_ledger import PaperOrderLedger
from src.paper_order_reconciliation import PaperOrderReconciler


def order(order_id: str, quantity: int = 10, fill_price: str = "100") -> PaperOrder:
    return PaperOrder(
        order_id=order_id,
        decision=AIDecision.BUY,
        quantity=quantity,
        fill_price=Decimal(fill_price),
        status=PaperOrderStatus.FILLED,
    )


def test_reconcile_matches_exact_ledger_snapshot() -> None:
    first = order("PAPER-1")
    second = order("PAPER-2", fill_price="101")
    ledger = PaperOrderLedger()
    ledger.record(first)
    ledger.record(second)

    result = PaperOrderReconciler().reconcile(ledger, (first, second))

    assert result.matched is True
    assert result.expected_count == 2
    assert result.recorded_count == 2
    assert result.missing_order_ids == ()
    assert result.unexpected_order_ids == ()
    assert result.mismatched_order_ids == ()


def test_reconcile_reports_missing_order() -> None:
    first = order("PAPER-1")
    second = order("PAPER-2")
    ledger = PaperOrderLedger()
    ledger.record(first)

    result = PaperOrderReconciler().reconcile(ledger, (first, second))

    assert result.matched is False
    assert result.missing_order_ids == ("PAPER-2",)


def test_reconcile_reports_unexpected_order() -> None:
    first = order("PAPER-1")
    unexpected = order("PAPER-2")
    ledger = PaperOrderLedger()
    ledger.record(first)
    ledger.record(unexpected)

    result = PaperOrderReconciler().reconcile(ledger, (first,))

    assert result.matched is False
    assert result.unexpected_order_ids == ("PAPER-2",)


def test_reconcile_reports_mismatched_record() -> None:
    recorded = order("PAPER-1", quantity=10)
    expected = order("PAPER-1", quantity=20)
    ledger = PaperOrderLedger()
    ledger.record(recorded)

    result = PaperOrderReconciler().reconcile(ledger, (expected,))

    assert result.matched is False
    assert result.mismatched_order_ids == ("PAPER-1",)


def test_reconcile_rejects_duplicate_expected_ids() -> None:
    first = order("PAPER-1")

    with pytest.raises(ValueError, match="duplicate order IDs"):
        PaperOrderReconciler().reconcile(PaperOrderLedger(), (first, first))


def test_reconcile_is_read_only() -> None:
    first = order("PAPER-1")
    ledger = PaperOrderLedger()
    ledger.record(first)

    PaperOrderReconciler().reconcile(ledger, (first,))

    assert ledger.snapshot() == (first,)
