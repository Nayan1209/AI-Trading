"""Deterministic PAPER-005 paper-position accounting boundary."""

from dataclasses import dataclass
from decimal import Decimal

from src.paper_execution import PaperOrder, PaperOrderStatus
from src.ai_analyst import AIDecision


@dataclass(frozen=True)
class PaperPosition:
    """Immutable position snapshot for one explicit position key."""

    position_key: str
    quantity: int
    average_entry_price: Decimal
    realized_pnl: Decimal


class PaperPositionLedger:
    """Apply filled paper orders to deterministic long-only position state."""

    def __init__(self) -> None:
        self._positions: dict[str, PaperPosition] = {}
        self._applied_order_ids: set[str] = set()

    def apply(self, position_key: str, order: PaperOrder) -> PaperPosition:
        """Apply one filled paper order and return the new immutable position."""
        if not isinstance(position_key, str) or not position_key.strip():
            raise ValueError("position_key must be a non-empty string")
        if not isinstance(order, PaperOrder):
            raise TypeError("order must be a PaperOrder")
        if order.status is not PaperOrderStatus.FILLED:
            raise ValueError("paper position accounting requires FILLED orders")
        if order.order_id in self._applied_order_ids:
            raise ValueError("paper order has already been applied")

        current = self._positions.get(position_key)
        if current is None:
            current = PaperPosition(
                position_key=position_key,
                quantity=0,
                average_entry_price=Decimal("0"),
                realized_pnl=Decimal("0"),
            )

        if order.decision is AIDecision.BUY:
            total_cost = (
                current.average_entry_price * Decimal(current.quantity)
                + order.fill_price * Decimal(order.quantity)
            )
            new_quantity = current.quantity + order.quantity
            new_average = total_cost / Decimal(new_quantity)
            updated = PaperPosition(
                position_key=position_key,
                quantity=new_quantity,
                average_entry_price=new_average,
                realized_pnl=current.realized_pnl,
            )
        elif order.decision is AIDecision.SELL:
            if current.quantity <= 0:
                raise ValueError("SELL requires an existing long paper position")
            if order.quantity > current.quantity:
                raise ValueError("SELL quantity exceeds existing paper position")
            realized = (
                order.fill_price - current.average_entry_price
            ) * Decimal(order.quantity)
            updated = PaperPosition(
                position_key=position_key,
                quantity=current.quantity - order.quantity,
                average_entry_price=(
                    current.average_entry_price
                    if current.quantity - order.quantity > 0
                    else Decimal("0")
                ),
                realized_pnl=current.realized_pnl + realized,
            )
        else:
            raise ValueError("paper position accounting requires BUY or SELL")

        self._positions[position_key] = updated
        self._applied_order_ids.add(order.order_id)
        return updated

    def get(self, position_key: str) -> PaperPosition | None:
        """Return one immutable position snapshot, or None when unseen."""
        return self._positions.get(position_key)

    def snapshot(self) -> tuple[PaperPosition, ...]:
        """Return deterministic immutable position snapshots ordered by key."""
        return tuple(self._positions[key] for key in sorted(self._positions))

    @property
    def applied_order_ids(self) -> tuple[str, ...]:
        """Return applied order IDs in deterministic sorted order."""
        return tuple(sorted(self._applied_order_ids))
