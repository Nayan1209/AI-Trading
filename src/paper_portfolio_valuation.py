"""Deterministic PAPER-007 paper-portfolio valuation boundary."""

from dataclasses import dataclass
from decimal import Decimal
from collections.abc import Mapping, Sequence

from src.paper_position_ledger import PaperPosition
from src.paper_position_valuation import (
    PaperPositionValuation,
    PaperPositionValuationEngine,
)


PNL_DECIMAL_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class PaperPortfolioValuation:
    """Immutable aggregate valuation for an explicit set of paper positions."""

    positions: tuple[PaperPositionValuation, ...]
    market_value: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal


class PaperPortfolioValuationEngine:
    """Aggregate deterministic valuations without mutating position state."""

    def __init__(self) -> None:
        self._position_engine = PaperPositionValuationEngine()

    def evaluate(
        self,
        positions: Sequence[PaperPosition],
        market_prices: Mapping[str, Decimal],
    ) -> PaperPortfolioValuation:
        """Return a deterministic portfolio valuation from immutable inputs."""
        if not isinstance(positions, Sequence) or isinstance(
            positions, (str, bytes)
        ):
            raise TypeError("positions must be a sequence of PaperPosition")
        if not isinstance(market_prices, Mapping):
            raise TypeError("market_prices must be a mapping")

        position_by_key: dict[str, PaperPosition] = {}
        for position in positions:
            if not isinstance(position, PaperPosition):
                raise TypeError("positions must contain only PaperPosition values")
            if position.position_key in position_by_key:
                raise ValueError("duplicate position_key")
            position_by_key[position.position_key] = position

        position_keys = set(position_by_key)
        price_keys = set(market_prices)
        missing = position_keys - price_keys
        unexpected = price_keys - position_keys
        if missing:
            raise ValueError("market_prices missing position key")
        if unexpected:
            raise ValueError("market_prices contains unexpected position key")

        valuations = tuple(
            self._position_engine.evaluate(position_by_key[key], market_prices[key])
            for key in sorted(position_by_key)
        )

        market_value = sum(
            (valuation.market_value for valuation in valuations), Decimal("0")
        )
        realized_pnl = sum(
            (valuation.realized_pnl for valuation in valuations), Decimal("0")
        ).quantize(PNL_DECIMAL_QUANTUM)
        unrealized_pnl = sum(
            (valuation.unrealized_pnl for valuation in valuations), Decimal("0")
        ).quantize(PNL_DECIMAL_QUANTUM)
        total_pnl = (realized_pnl + unrealized_pnl).quantize(PNL_DECIMAL_QUANTUM)

        return PaperPortfolioValuation(
            positions=valuations,
            market_value=market_value,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=total_pnl,
        )
