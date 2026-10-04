"""Deterministic PAPER-006 paper-position valuation boundary."""

from dataclasses import dataclass
from decimal import Decimal, localcontext

from src.paper_position_ledger import PaperPosition


POSITION_VALUATION_DECIMAL_PRECISION = 31
PNL_DECIMAL_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class PaperPositionValuation:
    """Immutable mark-to-market valuation for one paper position."""

    position_key: str
    quantity: int
    market_price: Decimal
    market_value: Decimal
    average_entry_price: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal


class PaperPositionValuationEngine:
    """Value PAPER-005 positions deterministically without mutating state."""

    def evaluate(
        self, position: PaperPosition, market_price: Decimal
    ) -> PaperPositionValuation:
        """Return a deterministic mark-to-market valuation snapshot."""
        if not isinstance(position, PaperPosition):
            raise TypeError("position must be a PaperPosition")
        if not isinstance(market_price, Decimal):
            raise TypeError("market_price must be a Decimal")
        if market_price <= Decimal("0"):
            raise ValueError("market_price must be positive")

        with localcontext() as context:
            context.prec = POSITION_VALUATION_DECIMAL_PRECISION
            market_value = market_price * Decimal(position.quantity)
            unrealized_pnl = (
                (market_price - position.average_entry_price)
                * Decimal(position.quantity)
            ).quantize(PNL_DECIMAL_QUANTUM)
            total_pnl = (position.realized_pnl + unrealized_pnl).quantize(
                PNL_DECIMAL_QUANTUM
            )

        return PaperPositionValuation(
            position_key=position.position_key,
            quantity=position.quantity,
            market_price=market_price,
            market_value=market_value,
            average_entry_price=position.average_entry_price,
            realized_pnl=position.realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=total_pnl,
        )
