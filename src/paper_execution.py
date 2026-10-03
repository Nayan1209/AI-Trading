"""Deterministic PAPER-001 simulation execution boundary."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
import hashlib

from src.ai_analyst import AIDecision
from src.trade_planner import TradePlan


class PaperOrderStatus(StrEnum):
    """Terminal status supported by the first paper-execution milestone."""

    FILLED = "FILLED"


@dataclass(frozen=True)
class PaperOrder:
    """Immutable simulated order/fill result."""

    order_id: str
    decision: AIDecision
    quantity: int
    fill_price: Decimal
    status: PaperOrderStatus


class PaperExecutionEngine:
    """Simulate approved trade plans without broker or network access."""

    def execute(
        self,
        plan: TradePlan,
        *,
        fill_price: Decimal,
        environment: str = "paper",
    ) -> PaperOrder:
        """Return a deterministic simulated fill for a valid paper order."""
        if environment != "paper":
            raise ValueError("paper execution requires environment='paper'")
        if not isinstance(plan, TradePlan):
            raise TypeError("plan must be a TradePlan")
        if plan.decision not in (AIDecision.BUY, AIDecision.SELL):
            raise ValueError("paper execution requires BUY or SELL plan")
        if plan.quantity <= 0:
            raise ValueError("paper execution quantity must be positive")
        if fill_price <= 0:
            raise ValueError("paper fill price must be positive")

        canonical = "|".join(
            (
                plan.decision.value,
                str(plan.entry),
                str(plan.stop_loss),
                str(plan.target),
                str(plan.quantity),
                str(plan.risk_budget),
                str(plan.estimated_risk),
                str(plan.notional_value),
                str(fill_price),
            )
        )
        order_id = "PAPER-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

        return PaperOrder(
            order_id=order_id,
            decision=plan.decision,
            quantity=plan.quantity,
            fill_price=fill_price,
            status=PaperOrderStatus.FILLED,
        )
