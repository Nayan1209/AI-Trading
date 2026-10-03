"""Deterministic tests for the AI-006 response parsing boundary."""

from decimal import Decimal

import pytest

from src.ai_model import AIModelResponse
from src.ai_response import AIModelResponseParser


BASE = {
    "decision": "BUY",
    "confidence": 0.82,
    "setup": "momentum continuation",
    "reason_codes": ["MOMENTUM", "BREAKOUT"],
    "entry": 100.25,
    "stop_loss": 98.50,
    "target": 104.00,
    "invalidation": "close below support",
}


def response(payload: dict[str, object] | None = None) -> AIModelResponse:
    import json

    body = payload or BASE
    return AIModelResponse(
        content=json.dumps(body),
        model_version="fake-model-v1",
        prompt_version="ai-004-v1",
    )


def test_parser_returns_validated_analysis() -> None:
    result = AIModelResponseParser.parse(response())

    assert result.decision.value == "BUY"
    assert result.confidence == Decimal("0.82")
    assert result.entry == Decimal("100.25")
    assert result.model_version == "fake-model-v1"
    assert result.prompt_version == "ai-004-v1"


def test_invalid_json_is_rejected() -> None:
    model_response = AIModelResponse(
        content="not-json",
        model_version="fake-model-v1",
        prompt_version="ai-004-v1",
    )

    with pytest.raises(ValueError, match="must be valid JSON"):
        AIModelResponseParser.parse(model_response)


def test_json_array_is_rejected() -> None:
    model_response = AIModelResponse(
        content="[]",
        model_version="fake-model-v1",
        prompt_version="ai-004-v1",
    )

    with pytest.raises(ValueError, match="must be an object"):
        AIModelResponseParser.parse(model_response)


def test_missing_required_field_is_rejected() -> None:
    payload = dict(BASE)
    del payload["invalidation"]

    with pytest.raises(ValueError, match="missing required fields: invalidation"):
        AIModelResponseParser.parse(response(payload))


def test_unsupported_field_is_rejected() -> None:
    payload = dict(BASE)
    payload["execute_order"] = True

    with pytest.raises(ValueError, match="unsupported fields: execute_order"):
        AIModelResponseParser.parse(response(payload))


def test_invalid_analysis_value_is_rejected() -> None:
    payload = dict(BASE)
    payload["confidence"] = 1.5

    with pytest.raises(ValueError, match="failed AI analysis validation"):
        AIModelResponseParser.parse(response(payload))


def test_model_metadata_is_taken_from_adapter_response() -> None:
    result = AIModelResponseParser.parse(response())

    assert result.model_version == "fake-model-v1"
    assert result.prompt_version == "ai-004-v1"
