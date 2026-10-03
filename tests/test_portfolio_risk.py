"""Deterministic tests for RISK-002."""

from decimal import Decimal

import pytest

from src.portfolio_risk import OpenPosition, PortfolioRiskGate


def position(symbol: str, notional: str) -> OpenPosition:
    return OpenPosition(symbol=symbol, notional_value=Decimal(notional))


def test_candidate_within_all_limits_is_approved() -> None:
    result = PortfolioRiskGate().evaluate(
        (position("RELIANCE", "10000"),),
        candidate_symbol="TCS",
        candidate_notional=Decimal("15000"),
        equity=Decimal("100000"),
        max_portfolio_exposure_pct=Decimal("50"),
        max_symbol_exposure_pct=Decimal("25"),
        max_open_positions=5,
    )

    assert result.approved is True
    assert result.projected_exposure == Decimal("25000")
    assert result.projected_symbol_exposure == Decimal("15000")
    assert result.projected_open_positions == 2


def test_portfolio_exposure_limit_is_rejected() -> None:
    with pytest.raises(ValueError, match="portfolio exposure"):
        PortfolioRiskGate().evaluate(
            (position("RELIANCE", "40000"),),
            candidate_symbol="TCS",
            candidate_notional=Decimal("15000"),
            equity=Decimal("100000"),
            max_portfolio_exposure_pct=Decimal("50"),
            max_symbol_exposure_pct=Decimal("50"),
            max_open_positions=5,
        )


def test_symbol_concentration_limit_is_rejected() -> None:
    with pytest.raises(ValueError, match="symbol concentration"):
        PortfolioRiskGate().evaluate(
            (position("RELIANCE", "15000"),),
            candidate_symbol="RELIANCE",
            candidate_notional=Decimal("15000"),
            equity=Decimal("100000"),
            max_portfolio_exposure_pct=Decimal("50"),
            max_symbol_exposure_pct=Decimal("25"),
            max_open_positions=5,
        )


def test_existing_symbol_does_not_consume_new_position_slot() -> None:
    result = PortfolioRiskGate().evaluate(
        (position("RELIANCE", "10000"), position("TCS", "10000")),
        candidate_symbol="TCS",
        candidate_notional=Decimal("5000"),
        equity=Decimal("100000"),
        max_portfolio_exposure_pct=Decimal("50"),
        max_symbol_exposure_pct=Decimal("20"),
        max_open_positions=2,
    )

    assert result.projected_open_positions == 2
    assert result.projected_symbol_exposure == Decimal("15000")


def test_new_symbol_cannot_exceed_open_position_limit() -> None:
    with pytest.raises(ValueError, match="maximum open positions"):
        PortfolioRiskGate().evaluate(
            (position("RELIANCE", "10000"), position("TCS", "10000")),
            candidate_symbol="INFY",
            candidate_notional=Decimal("5000"),
            equity=Decimal("100000"),
            max_portfolio_exposure_pct=Decimal("50"),
            max_symbol_exposure_pct=Decimal("20"),
            max_open_positions=2,
        )


def test_duplicate_current_symbols_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique symbols"):
        PortfolioRiskGate().evaluate(
            (position("RELIANCE", "10000"), position("RELIANCE", "5000")),
            candidate_symbol="TCS",
            candidate_notional=Decimal("5000"),
            equity=Decimal("100000"),
            max_portfolio_exposure_pct=Decimal("50"),
            max_symbol_exposure_pct=Decimal("20"),
            max_open_positions=5,
        )


def test_invalid_limits_are_rejected() -> None:
    with pytest.raises(ValueError, match="max_open_positions"):
        PortfolioRiskGate().evaluate(
            (),
            candidate_symbol="TCS",
            candidate_notional=Decimal("5000"),
            equity=Decimal("100000"),
            max_portfolio_exposure_pct=Decimal("50"),
            max_symbol_exposure_pct=Decimal("20"),
            max_open_positions=0,
        )


def test_result_is_immutable() -> None:
    result = PortfolioRiskGate().evaluate(
        (),
        candidate_symbol="TCS",
        candidate_notional=Decimal("5000"),
        equity=Decimal("100000"),
        max_portfolio_exposure_pct=Decimal("50"),
        max_symbol_exposure_pct=Decimal("20"),
        max_open_positions=5,
    )

    with pytest.raises((AttributeError, TypeError)):
        result.approved = False  # type: ignore[misc]
