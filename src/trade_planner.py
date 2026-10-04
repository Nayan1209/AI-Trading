"""Deterministic PLAN-001 trade-planning boundary."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.ai_analyst import AIDecision, AIAnalysis
from src.risk_engine import RiskEngine


@dataclass(frozen=True)
class TradePlan:
    """Immutable broker-independent order intent with explicit instrument identity."""

    decision: AIDecision
    entry: Decimal
    stop_loss: Decimal
    target: Decimal
    quantity: int
    risk_budget: Decimal
    estimated_risk: Decimal
    notional_value: Decimal
    reason: str
    internal_id: str = ""
    trading_symbol: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    client_order_id: str = field(default_factory=lambda: f"CLIENT-{uuid4().hex}")


class TradePlanner:
    """Build a deterministic trade plan without executing anything."""

    def __init__(self, risk_engine: RiskEngine | None = None) -> None:
        self._risk_engine = risk_engine or RiskEngine()

    def plan(
        self,
        analysis: AIAnalysis,
        *,
        equity: Decimal,
        risk_pct: Decimal,
        max_notional_pct: Decimal,
        lot_size: int = 1,
        internal_id: str,
        trading_symbol: str,
        client_order_id: str | None = None,
    ) -> TradePlan:
        """Return an immutable plan after the mandatory RISK-001 gate."""
        internal_id = internal_id.strip()
        trading_symbol = trading_symbol.strip()
        if not internal_id:
            raise ValueError("internal_id must not be empty")
        if not trading_symbol:
            raise ValueError("trading_symbol must not be empty")

        client_order_id = (client_order_id or f"CLIENT-{uuid4().hex}").strip()
        if not client_order_id:
            raise ValueError("client_order_id must not be empty")

        risk = self._risk_engine.evaluate(
            analysis,
            equity=equity,
            risk_pct=risk_pct,
            max_notional_pct=max_notional_pct,
            lot_size=lot_size,
        )

        if analysis.decision not in (AIDecision.BUY, AIDecision.SELL):
            raise ValueError("trade planning requires BUY or SELL")
        if analysis.entry is None or analysis.stop_loss is None or analysis.target is None:
            raise ValueError("trade planning requires entry, stop_loss and target")

        return TradePlan(
            decision=analysis.decision,
            entry=analysis.entry,
            stop_loss=analysis.stop_loss,
            target=analysis.target,
            quantity=risk.quantity,
            risk_budget=risk.risk_budget,
            estimated_risk=risk.estimated_risk,
            notional_value=risk.notional_value,
            reason="trade plan passed AI integrity and deterministic risk gates",
            internal_id=internal_id,
            trading_symbol=trading_symbol,
            created_at=datetime.now(timezone.utc),
            client_order_id=client_order_id,
        )
