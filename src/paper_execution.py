"""Deterministic PAPER-001 simulation execution boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
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
    """Immutable simulated order/fill result with explicit identity."""

    order_id: str
    internal_id: str
    trading_symbol: str
    client_order_id: str
    created_at: datetime
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
        if not plan.internal_id.strip():
            raise ValueError("paper execution requires internal_id")
        if not plan.trading_symbol.strip():
            raise ValueError("paper execution requires trading_symbol")
        if not plan.client_order_id.strip():
            raise ValueError("paper execution requires client_order_id")

        canonical = "|".join(
            (
                plan.internal_id,
                plan.trading_symbol,
                plan.client_order_id,
                plan.created_at.isoformat(),
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
        order_id = "PAPER-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

        return PaperOrder(
            order_id=order_id,
            internal_id=plan.internal_id,
            trading_symbol=plan.trading_symbol,
            client_order_id=plan.client_order_id,
            created_at=datetime.now(timezone.utc),
            decision=plan.decision,
            quantity=plan.quantity,
            fill_price=fill_price,
            status=PaperOrderStatus.FILLED,
        )
