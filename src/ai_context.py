"""Deterministic signal-to-AI context adapter for AI-002."""

from typing import Mapping

from src.ai_analyst import AIAnalysisContext
from src.signal_engine import SignalCandidate


class AIAnalysisContextBuilder:
    """Build the structured AI-001 context from validated signal output."""

    def build(
        self,
        signal: SignalCandidate,
        *,
        timeframe: str,
        market_features: Mapping[str, object],
        relevant_context: Mapping[str, object],
        portfolio_constraints: Mapping[str, object],
    ) -> AIAnalysisContext:
        """Convert one deterministic signal into an AI analysis context.

        All market/context values are caller supplied. This adapter never
        fetches data, calls an AI provider, changes risk controls, or executes
        orders.
        """
        return AIAnalysisContext(
            instrument=signal.internal_id,
            timeframe=timeframe,
            market_features=dict(market_features),
            signal_features={
                "rank": signal.rank,
                "trading_symbol": signal.trading_symbol,
                "signal_type": signal.signal_type.value,
                "direction": signal.direction.value,
                "strategy_score": signal.strategy_score,
                "reason_codes": signal.reason_codes,
            },
            relevant_context=dict(relevant_context),
            portfolio_constraints=dict(portfolio_constraints),
        )
