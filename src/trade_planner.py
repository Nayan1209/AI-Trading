"""Deterministic PLAN-001 trade-planning boundary."""

from dataclasses import dataclass
from decimal import Decimal

from src.ai_analyst import AIDecision, AIAnalysis
from src.risk_engine import RiskEngine


@dataclass(frozen=True)
class TradePlan:
    """Immutable broker-independent order intent."""

    decision: AIDecision
    entry: Decimal
    stop_loss: Decimal
    target: Decimal
    quantity: int
    risk_budget: Decimal
    estimated_risk: Decimal
    notional_value: Decimal
    reason: str


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
    ) -> TradePlan:
        """Return an immutable plan after the mandatory RISK-001 gate."""
        risk = self._risk_engine.evaluate(
            analysis,
            equity=equity,
            risk_pct=risk_pct,
            max_notional_pct=max_notional_pct,
            lot_size=lot_size,
        )

        assert analysis.decision in (AIDecision.BUY, AIDecision.SELL)
        assert analysis.entry is not None
        assert analysis.stop_loss is not None
        assert analysis.target is not None

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
        )
