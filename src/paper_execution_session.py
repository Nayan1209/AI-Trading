"""Deterministic PAPER-004 orchestration for a paper execution session."""

from dataclasses import dataclass
from decimal import Decimal

from src.paper_execution import PaperExecutionEngine, PaperOrder
from src.paper_order_ledger import PaperOrderLedger
from src.paper_order_reconciliation import PaperOrderReconciler, PaperReconciliationResult
from src.trade_planner import TradePlan


@dataclass(frozen=True)
class PaperExecutionSessionResult:
    """Immutable result of one complete paper-execution session."""

    order: PaperOrder
    reconciliation: PaperReconciliationResult


class PaperExecutionSession:
    """Compose execution, ledger recording, and read-only reconciliation."""

    def __init__(
        self,
        engine: PaperExecutionEngine | None = None,
        ledger: PaperOrderLedger | None = None,
        reconciler: PaperOrderReconciler | None = None,
    ) -> None:
        self._engine = engine or PaperExecutionEngine()
        self._ledger = ledger or PaperOrderLedger()
        self._reconciler = reconciler or PaperOrderReconciler()

    @property
    def ledger(self) -> PaperOrderLedger:
        """Return the session ledger for subsequent read-only inspection."""
        return self._ledger

    def execute(
        self,
        plan: TradePlan,
        *,
        fill_price: Decimal,
    ) -> PaperExecutionSessionResult:
        """Execute, record, and reconcile one deterministic paper order."""
        before = self._ledger.snapshot()
        order = self._engine.execute(plan, fill_price=fill_price)
        self._ledger.record(order)
        expected = before + (order,)
        reconciliation = self._reconciler.reconcile(self._ledger, expected)
        return PaperExecutionSessionResult(
            order=order,
            reconciliation=reconciliation,
        )
