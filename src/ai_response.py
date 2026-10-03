"""Deterministic model-response parsing boundary for AI-006."""

import json
from decimal import Decimal
from typing import Any

from src.ai_analyst import AIAnalysis
from src.ai_model import AIModelResponse


_ALLOWED_FIELDS = frozenset(
    {
        "decision",
        "confidence",
        "setup",
        "reason_codes",
        "entry",
        "stop_loss",
        "target",
        "invalidation",
    }
)


class AIModelResponseParser:
    """Convert one untrusted model response into validated AIAnalysis."""

    @staticmethod
    def _reject_constant(value: str) -> None:
        raise ValueError(f"invalid JSON constant: {value}")

    @classmethod
    def parse(cls, response: AIModelResponse) -> AIAnalysis:
        """Parse strict JSON model output and validate the AI-001 contract."""
        if not isinstance(response, AIModelResponse):
            raise TypeError("response must be an AIModelResponse")

        try:
            payload: Any = json.loads(
                response.content,
                parse_float=Decimal,
                parse_int=Decimal,
                parse_constant=cls._reject_constant,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError("model response must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("model response JSON must be an object")

        unexpected = set(payload) - _ALLOWED_FIELDS
        if unexpected:
            names = ", ".join(sorted(str(name) for name in unexpected))
            raise ValueError(f"model response contains unsupported fields: {names}")

        missing = _ALLOWED_FIELDS - set(payload)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"model response is missing required fields: {names}")

        structured = dict(payload)
        structured["model_version"] = response.model_version
        structured["prompt_version"] = response.prompt_version

        try:
            return AIAnalysis.model_validate(structured)
        except Exception as exc:
            raise ValueError("model response failed AI analysis validation") from exc
