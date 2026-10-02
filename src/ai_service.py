"""Deterministic AI analysis orchestration for AI-003."""

from typing import Mapping

from src.ai_analyst import AIAnalysis, AIAnalyst
from src.ai_context import AIAnalysisContextBuilder
from src.signal_engine import SignalCandidate


class AIAnalysisService:
    """Compose signal-to-context mapping with the validated AI analyst."""

    def __init__(
        self,
        analyst: AIAnalyst,
        context_builder: AIAnalysisContextBuilder | None = None,
    ) -> None:
        self._analyst = analyst
        self._context_builder = context_builder or AIAnalysisContextBuilder()

    def analyze_signal(
        self,
        signal: SignalCandidate,
        *,
        timeframe: str,
        market_features: Mapping[str, object],
        relevant_context: Mapping[str, object],
        portfolio_constraints: Mapping[str, object],
    ) -> AIAnalysis:
        """Build AI-001 context from a signal and return validated analysis."""
        context = self._context_builder.build(
            signal,
            timeframe=timeframe,
            market_features=market_features,
            relevant_context=relevant_context,
            portfolio_constraints=portfolio_constraints,
        )
        return self._analyst.analyze(context)
