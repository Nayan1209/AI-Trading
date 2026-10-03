from decimal import Decimal

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperOrder, PaperOrderStatus
from src.paper_position_ledger import PaperPositionLedger


def order(order_id: str, decision: AIDecision, quantity: int, price: str) -> PaperOrder:
    return PaperOrder(
        order_id=order_id,
        decision=decision,
        quantity=quantity,
        fill_price=Decimal(price),
        status=PaperOrderStatus.FILLED,
    )


def test_buy_uses_weighted_average_entry_price() -> None:
    ledger = PaperPositionLedger()

    ledger.apply("NSE:CASH:RELIANCE", order("B1", AIDecision.BUY, 10, "100"))
    position = ledger.apply(
        "NSE:CASH:RELIANCE", order("B2", AIDecision.BUY, 20, "110")
    )

    assert position.quantity == 30
    assert position.average_entry_price == Decimal("106.6666666666666666666666666667")
    assert position.realized_pnl == Decimal("0")


def test_sell_realizes_pnl_against_average_entry_price() -> None:
    ledger = PaperPositionLedger()
    ledger.apply("RELIANCE", order("B1", AIDecision.BUY, 10, "100"))

    position = ledger.apply("RELIANCE", order("S1", AIDecision.SELL, 4, "115"))

    assert position.quantity == 6
    assert position.average_entry_price == Decimal("100")
    assert position.realized_pnl == Decimal("60")


def test_closing_position_resets_average_price_but_keeps_realized_pnl() -> None:
    ledger = PaperPositionLedger()
    ledger.apply("RELIANCE", order("B1", AIDecision.BUY, 10, "100"))

    position = ledger.apply("RELIANCE", order("S1", AIDecision.SELL, 10, "90"))

    assert position.quantity == 0
    assert position.average_entry_price == Decimal("0")
    assert position.realized_pnl == Decimal("-100")


def test_sell_cannot_open_or_overdraw_a_long_position() -> None:
    ledger = PaperPositionLedger()

    with pytest.raises(ValueError, match="existing long paper position"):
        ledger.apply("RELIANCE", order("S1", AIDecision.SELL, 1, "100"))

    ledger.apply("RELIANCE", order("B1", AIDecision.BUY, 5, "100"))
    with pytest.raises(ValueError, match="exceeds existing paper position"):
        ledger.apply("RELIANCE", order("S2", AIDecision.SELL, 6, "100"))


def test_duplicate_order_is_rejected_without_mutating_position() -> None:
    ledger = PaperPositionLedger()
    buy = order("B1", AIDecision.BUY, 5, "100")
    ledger.apply("RELIANCE", buy)

    with pytest.raises(ValueError, match="already been applied"):
        ledger.apply("RELIANCE", buy)

    assert ledger.get("RELIANCE").quantity == 5
    assert ledger.applied_order_ids == ("B1",)


def test_snapshot_is_deterministic_and_immutable() -> None:
    ledger = PaperPositionLedger()
    ledger.apply("ZETA", order("Z1", AIDecision.BUY, 1, "10"))
    ledger.apply("ALPHA", order("A1", AIDecision.BUY, 1, "20"))

    snapshot = ledger.snapshot()

    assert tuple(position.position_key for position in snapshot) == ("ALPHA", "ZETA")
    assert isinstance(snapshot, tuple)


def test_invalid_order_type_and_key_are_rejected() -> None:
    ledger = PaperPositionLedger()

    with pytest.raises(ValueError, match="non-empty string"):
        ledger.apply("", order("B1", AIDecision.BUY, 1, "100"))

    with pytest.raises(TypeError, match="PaperOrder"):
        ledger.apply("RELIANCE", object())

    invalid_status = PaperOrder(
        order_id="R1",
        decision=AIDecision.BUY,
        quantity=1,
        fill_price=Decimal("100"),
        status="FILLED",  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="FILLED orders"):
        ledger.apply("RELIANCE", invalid_status)
