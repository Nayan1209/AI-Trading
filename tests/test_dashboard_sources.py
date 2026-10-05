from datetime import datetime, timezone
from decimal import Decimal

from src.ai_analyst import AIDecision
from src.dashboard_sources import paper_snapshot
from src.paper_execution import PaperOrder, PaperOrderStatus


def _order(order_id: str, side: AIDecision, quantity: int, price: str) -> PaperOrder:
    return PaperOrder(
        order_id=order_id,
        client_order_id=f"CLIENT-{order_id}",
        internal_id="instrument-1",
        trading_symbol="RELIANCE",
        decision=side,
        quantity=quantity,
        fill_price=Decimal(price),
        status=PaperOrderStatus.FILLED,
        created_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
    )


def test_paper_snapshot_reconstructs_open_positions_and_realized_pnl() -> None:
    snapshot = paper_snapshot(
        (
            _order("BUY-1", AIDecision.BUY, 5, "100"),
            _order("SELL-1", AIDecision.SELL, 2, "105"),
        ),
        source="test",
        detail="test source",
    )

    assert snapshot["order_count"] == 2
    assert snapshot["position_count"] == 1
    assert snapshot["realized_pnl"] == "10"
    assert snapshot["unrealized_pnl"] is None
    assert snapshot["positions"] == [
        {
            "position_key": "instrument-1",
            "symbol": "RELIANCE",
            "quantity": 3,
            "average_entry_price": "100",
            "realized_pnl": "10",
        }
    ]
    assert [order["side"] for order in snapshot["orders"]] == ["SELL", "BUY"]


def test_paper_snapshot_does_not_invent_a_mark_for_empty_state() -> None:
    snapshot = paper_snapshot((), source="test", detail="empty")

    assert snapshot["status"] == "available"
    assert snapshot["positions"] == []
    assert snapshot["orders"] == []
    assert snapshot["realized_pnl"] == "0"
    assert snapshot["unrealized_pnl"] is None
