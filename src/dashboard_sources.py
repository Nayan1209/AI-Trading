"""Read-only dashboard projections for paper execution state."""

from collections.abc import Sequence
from decimal import Decimal

from src.paper_execution import PaperOrder
from src.paper_position_ledger import PaperPositionLedger


def paper_snapshot(
    orders: Sequence[PaperOrder],
    *,
    source: str,
    detail: str,
) -> dict[str, object]:
    """Project immutable fills into positions and realized P&L without writes."""
    ledger = PaperPositionLedger()
    symbols_by_position: dict[str, str] = {}
    for order in orders:
        position_key = order.internal_id or order.trading_symbol
        ledger.apply(position_key, order)
        symbols_by_position[position_key] = order.trading_symbol

    all_positions = ledger.snapshot()
    positions = tuple(position for position in all_positions if position.quantity > 0)
    recent_orders = tuple(reversed(tuple(orders)))[0:10]
    return {
        "status": "available",
        "source": source,
        "detail": detail,
        "order_count": len(orders),
        "position_count": sum(position.quantity > 0 for position in positions),
        "realized_pnl": str(
            sum((position.realized_pnl for position in all_positions), Decimal("0"))
        ),
        "unrealized_pnl": None,
        "positions": [
            {
                "position_key": position.position_key,
                "symbol": symbols_by_position.get(position.position_key, position.position_key),
                "quantity": position.quantity,
                "average_entry_price": str(position.average_entry_price),
                "realized_pnl": str(position.realized_pnl),
            }
            for position in positions
        ],
        "orders": [
            {
                "order_id": order.order_id,
                "symbol": order.trading_symbol,
                "side": order.decision.value,
                "quantity": order.quantity,
                "fill_price": str(order.fill_price),
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
            }
            for order in recent_orders
        ],
    }
