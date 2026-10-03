"""Deterministic PAPER-003 reconciliation for the paper-order ledger."""

from dataclasses import dataclass

from src.paper_execution import PaperOrder
from src.paper_order_ledger import PaperOrderLedger


@dataclass(frozen=True)
class PaperReconciliationResult:
    """Immutable reconciliation outcome."""

    matched: bool
    expected_count: int
    recorded_count: int
    missing_order_ids: tuple[str, ...]
    unexpected_order_ids: tuple[str, ...]
    mismatched_order_ids: tuple[str, ...]


class PaperOrderReconciler:
    """Compare expected paper orders with the in-process ledger."""

    def reconcile(
        self,
        ledger: PaperOrderLedger,
        expected: tuple[PaperOrder, ...],
    ) -> PaperReconciliationResult:
        """Return a deterministic, read-only reconciliation result."""
        if not isinstance(ledger, PaperOrderLedger):
            raise TypeError("ledger must be a PaperOrderLedger")
        if not isinstance(expected, tuple):
            raise TypeError("expected must be a tuple of PaperOrder")
        if any(not isinstance(order, PaperOrder) for order in expected):
            raise TypeError("expected must contain only PaperOrder values")

        expected_ids = tuple(order.order_id for order in expected)
        if len(set(expected_ids)) != len(expected_ids):
            raise ValueError("expected orders contain duplicate order IDs")

        recorded = ledger.snapshot()
        recorded_by_id = {order.order_id: order for order in recorded}
        expected_by_id = {order.order_id: order for order in expected}

        missing = tuple(order_id for order_id in expected_ids if order_id not in recorded_by_id)
        unexpected = tuple(order.order_id for order in recorded if order.order_id not in expected_by_id)
        mismatched = tuple(
            order_id
            for order_id in expected_ids
            if order_id in recorded_by_id and recorded_by_id[order_id] != expected_by_id[order_id]
        )

        return PaperReconciliationResult(
            matched=not missing and not unexpected and not mismatched,
            expected_count=len(expected),
            recorded_count=len(recorded),
            missing_order_ids=missing,
            unexpected_order_ids=unexpected,
            mismatched_order_ids=mismatched,
        )
