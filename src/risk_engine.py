"""Deterministic RISK-001 position-sizing safety gate."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

from src.ai_analyst import AIDecision, AIAnalysis
from src.ai_integrity import AIAnalysisIntegrityGate


@dataclass(frozen=True)
class RiskDecision:
    """Bounded planning result produced by the deterministic risk engine."""

    approved: bool
    quantity: int
    risk_budget: Decimal
    estimated_risk: Decimal
    notional_value: Decimal
    reason: str


class RiskEngine:
    """Calculate a bounded, lot-aligned quantity without executing anything."""

    @staticmethod
    def _floor_to_lot(quantity: Decimal, lot_size: int) -> int:
        lots = (quantity / Decimal(lot_size)).to_integral_value(rounding=ROUND_DOWN)
        return int(lots) * lot_size

    def evaluate(
        self,
        analysis: AIAnalysis,
        *,
        equity: Decimal,
        risk_pct: Decimal,
        max_notional_pct: Decimal,
        lot_size: int = 1,
    ) -> RiskDecision:
        """Validate AI output and return a deterministic bounded quantity."""
        analysis = AIAnalysisIntegrityGate.validate(analysis)

        if analysis.decision not in (AIDecision.BUY, AIDecision.SELL):
            raise ValueError("risk engine requires BUY or SELL analysis")
        if equity <= 0:
            raise ValueError("equity must be positive")
        if not (Decimal("0") < risk_pct <= Decimal("100")):
            raise ValueError("risk_pct must be greater than 0 and less than or equal to 100")
        if not (Decimal("0") < max_notional_pct <= Decimal("100")):
            raise ValueError("max_notional_pct must be greater than 0 and less than or equal to 100")
        if lot_size < 1:
            raise ValueError("lot_size must be at least 1")

        assert analysis.entry is not None
        assert analysis.stop_loss is not None

        entry = analysis.entry
        stop = analysis.stop_loss
        if entry <= 0 or stop <= 0:
            raise ValueError("entry and stop_loss must be positive")

        per_unit_risk = abs(entry - stop)
        risk_budget = equity * risk_pct / Decimal("100")
        max_notional = equity * max_notional_pct / Decimal("100")

        risk_quantity = risk_budget / per_unit_risk
        notional_quantity = max_notional / entry
        quantity = self._floor_to_lot(min(risk_quantity, notional_quantity), lot_size)

        if quantity < lot_size:
            raise ValueError("risk limits produce zero executable quantity")

        estimated_risk = per_unit_risk * Decimal(quantity)
        notional_value = entry * Decimal(quantity)

        return RiskDecision(
            approved=True,
            quantity=quantity,
            risk_budget=risk_budget,
            estimated_risk=estimated_risk,
            notional_value=notional_value,
            reason="quantity is within explicit risk and notional limits",
        )
