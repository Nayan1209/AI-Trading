"""Provider-independent AI analyst boundary for AI-001.

This module validates the structured context entering an AI model and the
structured analysis returned by that model. It deliberately contains no live
model, web/news, broker, risk, or execution integration.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AIDecision(StrEnum):
    """Allowed decisions returned by the AI analyst."""

    BUY = "BUY"
    SELL = "SELL"
    WATCH = "WATCH"
    NO_TRADE = "NO_TRADE"


class AIAnalysisContext(BaseModel):
    """Minimum structured context permitted into an AI analysis call."""

    model_config = ConfigDict(frozen=True)

    instrument: str
    timeframe: str
    market_features: Mapping[str, object]
    signal_features: Mapping[str, object]
    relevant_context: Mapping[str, object]
    portfolio_constraints: Mapping[str, object]

    @field_validator("instrument", "timeframe")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("instrument and timeframe must not be empty")
        return value


class AIAnalysis(BaseModel):
    """Validated model output passed to later deterministic risk stages."""

    model_config = ConfigDict(frozen=True)

    decision: AIDecision
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    setup: str
    reason_codes: tuple[str, ...]
    entry: Decimal | None = None
    stop_loss: Decimal | None = None
    target: Decimal | None = None
    invalidation: str
    model_version: str
    prompt_version: str

    @field_validator("setup", "invalidation", "model_version", "prompt_version")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("analysis text and version fields must not be empty")
        return value

    @field_validator("reason_codes")
    @classmethod
    def non_empty_reason_codes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or any(not code.strip() for code in value):
            raise ValueError("reason_codes must not be empty")
        return tuple(code.strip() for code in value)

    @field_validator("entry", "stop_loss", "target")
    @classmethod
    def positive_prices(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value <= 0:
            raise ValueError("analysis prices must be positive")
        return value


class AIAnalysisProvider(Protocol):
    """Provider contract for a future model adapter."""

    def analyze(self, context: AIAnalysisContext) -> AIAnalysis:
        """Return structured analysis without performing execution."""
        ...


class AIAnalyst:
    """Validate the AI-001 boundary around a model provider."""

    def __init__(self, provider: AIAnalysisProvider):
        self._provider = provider

    def analyze(self, context: AIAnalysisContext) -> AIAnalysis:
        """Analyze validated context and return validated structured output."""
        validated_context = AIAnalysisContext.model_validate(context)
        result = self._provider.analyze(validated_context)
        validated_result = AIAnalysis.model_validate(result)
        return validated_result
