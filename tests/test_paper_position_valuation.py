from decimal import Decimal

import pytest

from src.paper_position_ledger import PaperPosition
from src.paper_position_valuation import PaperPositionValuationEngine


def position(
    quantity: int = 30,
    average_entry_price: str = "106.6666666666666666666666666667",
    realized_pnl: str = "60",
) -> PaperPosition:
    return PaperPosition(
        position_key="NSE:CASH:RELIANCE",
        quantity=quantity,
        average_entry_price=Decimal(average_entry_price),
        realized_pnl=Decimal(realized_pnl),
    )


def test_valuation_calculates_market_value_unrealized_and_total_pnl() -> None:
    result = PaperPositionValuationEngine().evaluate(position(), Decimal("120"))

    assert result.quantity == 30
    assert result.market_price == Decimal("120")
    assert result.market_value == Decimal("3600")
    assert result.average_entry_price == Decimal("106.6666666666666666666666666667")
    assert result.realized_pnl == Decimal("60")
    assert result.unrealized_pnl == Decimal("400")
    assert result.total_pnl == Decimal("460")


def test_valuation_supports_loss_without_mutating_position() -> None:
    source = position(quantity=10, average_entry_price="100", realized_pnl="25")

    result = PaperPositionValuationEngine().evaluate(source, Decimal("90"))

    assert result.market_value == Decimal("900")
    assert result.unrealized_pnl == Decimal("-100")
    assert result.total_pnl == Decimal("-75")
    assert source.quantity == 10
    assert source.average_entry_price == Decimal("100")
    assert source.realized_pnl == Decimal("25")


def test_zero_quantity_has_zero_market_and_unrealized_value() -> None:
    source = position(quantity=0, average_entry_price="0", realized_pnl="-100")

    result = PaperPositionValuationEngine().evaluate(source, Decimal("150"))

    assert result.market_value == Decimal("0")
    assert result.unrealized_pnl == Decimal("0")
    assert result.realized_pnl == Decimal("-100")
    assert result.total_pnl == Decimal("-100")


def test_non_positive_market_price_is_rejected() -> None:
    engine = PaperPositionValuationEngine()

    with pytest.raises(ValueError, match="market_price must be positive"):
        engine.evaluate(position(), Decimal("0"))

    with pytest.raises(ValueError, match="market_price must be positive"):
        engine.evaluate(position(), Decimal("-1"))


def test_invalid_inputs_are_rejected() -> None:
    engine = PaperPositionValuationEngine()

    with pytest.raises(TypeError, match="PaperPosition"):
        engine.evaluate(object(), Decimal("100"))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Decimal"):
        engine.evaluate(position(), 100)  # type: ignore[arg-type]
