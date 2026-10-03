"""Deterministic post-parsing integrity gate for AI-007."""

from src.ai_analyst import AIDecision, AIAnalysis


class AIAnalysisIntegrityGate:
    """Check internal analysis coherence without making risk decisions."""

    @staticmethod
    def validate(analysis: AIAnalysis) -> AIAnalysis:
        """Return the same validated analysis when its price semantics are coherent."""
        if not isinstance(analysis, AIAnalysis):
            raise TypeError("analysis must be an AIAnalysis")

        prices = (analysis.entry, analysis.stop_loss, analysis.target)

        if analysis.decision in (AIDecision.BUY, AIDecision.SELL):
            if any(price is None for price in prices):
                raise ValueError("BUY/SELL analysis requires entry, stop_loss, and target")

            entry = analysis.entry
            stop_loss = analysis.stop_loss
            target = analysis.target
            assert entry is not None
            assert stop_loss is not None
            assert target is not None

            if analysis.decision is AIDecision.BUY and not (stop_loss < entry < target):
                raise ValueError("BUY analysis requires stop_loss < entry < target")

            if analysis.decision is AIDecision.SELL and not (target < entry < stop_loss):
                raise ValueError("SELL analysis requires target < entry < stop_loss")

            return analysis

        if any(price is not None for price in prices):
            raise ValueError("WATCH/NO_TRADE analysis must not contain execution prices")

        return analysis
