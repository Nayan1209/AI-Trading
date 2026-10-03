"""Deterministic RISK-002 portfolio exposure safety gate."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class OpenPosition:
    """Minimal broker-independent representation of an open position."""

    symbol: str
    notional_value: Decimal


@dataclass(frozen=True)
class PortfolioRiskDecision:
    """Immutable result produced after the RISK-002 portfolio gate passes."""

    approved: bool
    projected_exposure: Decimal
    projected_symbol_exposure: Decimal
    projected_open_positions: int
    max_portfolio_exposure: Decimal
    max_symbol_exposure: Decimal
    reason: str


class PortfolioRiskGate:
    """Validate portfolio exposure and concentration without execution side effects."""

    def evaluate(
        self,
        positions: Iterable[OpenPosition],
        *,
        candidate_symbol: str,
        candidate_notional: Decimal,
        equity: Decimal,
        max_portfolio_exposure_pct: Decimal,
        max_symbol_exposure_pct: Decimal,
        max_open_positions: int,
    ) -> PortfolioRiskDecision:
        """Return an approved deterministic portfolio decision or raise on violation."""
        if equity <= 0:
            raise ValueError("equity must be positive")
        if not (Decimal("0") < max_portfolio_exposure_pct <= Decimal("100")):
            raise ValueError("max_portfolio_exposure_pct must be greater than 0 and less than or equal to 100")
        if not (Decimal("0") < max_symbol_exposure_pct <= Decimal("100")):
            raise ValueError("max_symbol_exposure_pct must be greater than 0 and less than or equal to 100")
        if max_open_positions < 1:
            raise ValueError("max_open_positions must be at least 1")
        if not candidate_symbol.strip():
            raise ValueError("candidate_symbol must not be empty")
        if candidate_notional <= 0:
            raise ValueError("candidate_notional must be positive")

        current = tuple(positions)
        symbols = [position.symbol.strip() for position in current]
        if any(not symbol for symbol in symbols):
            raise ValueError("position symbols must not be empty")
        if len(symbols) != len(set(symbols)):
            raise ValueError("current positions must contain unique symbols")
        if any(position.notional_value <= 0 for position in current):
            raise ValueError("position notional values must be positive")

        symbol = candidate_symbol.strip()
        existing_exposure = sum(
            (position.notional_value for position in current), Decimal("0")
        )
        existing_symbol_exposure = sum(
            (position.notional_value for position in current if position.symbol.strip() == symbol),
            Decimal("0"),
        )
        projected_exposure = existing_exposure + candidate_notional
        projected_symbol_exposure = existing_symbol_exposure + candidate_notional
        projected_open_positions = len(symbols) + (0 if symbol in symbols else 1)

        max_portfolio_exposure = equity * max_portfolio_exposure_pct / Decimal("100")
        max_symbol_exposure = equity * max_symbol_exposure_pct / Decimal("100")

        if projected_exposure > max_portfolio_exposure:
            raise ValueError("portfolio exposure exceeds configured maximum")
        if projected_symbol_exposure > max_symbol_exposure:
            raise ValueError("symbol concentration exceeds configured maximum")
        if projected_open_positions > max_open_positions:
            raise ValueError("maximum open positions would be exceeded")

        return PortfolioRiskDecision(
            approved=True,
            projected_exposure=projected_exposure,
            projected_symbol_exposure=projected_symbol_exposure,
            projected_open_positions=projected_open_positions,
            max_portfolio_exposure=max_portfolio_exposure,
            max_symbol_exposure=max_symbol_exposure,
            reason="candidate is within explicit portfolio exposure, concentration, and position-count limits",
        )
