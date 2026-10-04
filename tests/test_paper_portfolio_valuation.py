from decimal import Decimal

import pytest

from src.paper_position_ledger import PaperPosition
from src.paper_portfolio_valuation import PaperPortfolioValuationEngine


def position(
    key: str,
    quantity: int = 10,
    average_entry_price: str = "100",
    realized_pnl: str = "0",
) -> PaperPosition:
    return PaperPosition(
        position_key=key,
        quantity=quantity,
        average_entry_price=Decimal(average_entry_price),
        realized_pnl=Decimal(realized_pnl),
    )


def test_portfolio_aggregates_positions_deterministically() -> None:
    positions = (
        position("NSE:CASH:TCS", 20, "200", "10"),
        position("NSE:CASH:RELIANCE", 30, "100", "60"),
    )

    result = PaperPortfolioValuationEngine().evaluate(
        positions,
        {
            "NSE:CASH:RELIANCE": Decimal("120"),
            "NSE:CASH:TCS": Decimal("190"),
        },
    )

    assert tuple(item.position_key for item in result.positions) == (
        "NSE:CASH:RELIANCE",
        "NSE:CASH:TCS",
    )
    assert result.market_value == Decimal("9300")
    assert result.realized_pnl == Decimal("70")
    assert result.unrealized_pnl == Decimal("400")
    assert result.total_pnl == Decimal("470")


def test_empty_portfolio_has_zero_aggregates() -> None:
    result = PaperPortfolioValuationEngine().evaluate((), {})

    assert result.positions == ()
    assert result.market_value == Decimal("0")
    assert result.realized_pnl == Decimal("0.00")
    assert result.unrealized_pnl == Decimal("0.00")
    assert result.total_pnl == Decimal("0.00")


def test_market_prices_must_match_position_keys() -> None:
    engine = PaperPortfolioValuationEngine()
    positions = (position("NSE:CASH:RELIANCE"),)

    with pytest.raises(ValueError, match="missing position key"):
        engine.evaluate(positions, {})

    with pytest.raises(ValueError, match="unexpected position key"):
        engine.evaluate(positions, {"NSE:CASH:TCS": Decimal("100")})


def test_duplicate_position_keys_are_rejected() -> None:
    engine = PaperPortfolioValuationEngine()
    positions = (
        position("NSE:CASH:RELIANCE"),
        position("NSE:CASH:RELIANCE", 20),
    )

    with pytest.raises(ValueError, match="duplicate position_key"):
        engine.evaluate(positions, {"NSE:CASH:RELIANCE": Decimal("120")})


def test_invalid_market_price_is_rejected() -> None:
    engine = PaperPortfolioValuationEngine()
    positions = (position("NSE:CASH:RELIANCE"),)

    with pytest.raises(ValueError, match="market_price must be positive"):
        engine.evaluate(positions, {"NSE:CASH:RELIANCE": Decimal("0")})

    with pytest.raises(ValueError, match="market_price must be positive"):
        engine.evaluate(positions, {"NSE:CASH:RELIANCE": Decimal("-1")})


def test_invalid_inputs_are_rejected() -> None:
    engine = PaperPortfolioValuationEngine()

    with pytest.raises(TypeError, match="positions must be a sequence"):
        engine.evaluate(object(), {})  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="market_prices must be a mapping"):
        engine.evaluate((), ())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="only PaperPosition"):
        engine.evaluate((object(),), {})  # type: ignore[arg-type]
