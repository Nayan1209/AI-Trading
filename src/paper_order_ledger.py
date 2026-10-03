"""Deterministic PAPER-002 ledger for simulated paper orders."""

from dataclasses import dataclass, field

from src.paper_execution import PaperOrder


@dataclass
class PaperOrderLedger:
    """Keep an immutable-order history with duplicate protection."""

    _orders: list[PaperOrder] = field(default_factory=list)

    def record(self, order: PaperOrder) -> PaperOrder:
        """Record a paper order exactly once and return the original order."""
        if not isinstance(order, PaperOrder):
            raise TypeError("order must be a PaperOrder")
        if any(existing.order_id == order.order_id for existing in self._orders):
            raise ValueError(f"paper order already recorded: {order.order_id}")
        self._orders.append(order)
        return order

    def get(self, order_id: str) -> PaperOrder:
        """Return a recorded order by deterministic order identifier."""
        for order in self._orders:
            if order.order_id == order_id:
                return order
        raise KeyError(order_id)

    def snapshot(self) -> tuple[PaperOrder, ...]:
        """Return an immutable snapshot preserving insertion order."""
        return tuple(self._orders)
