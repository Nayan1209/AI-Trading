"""Deterministic tests for the AI-005 model adapter boundary."""

import pytest

from src.ai_model import AIModelGateway, AIModelResponse
from src.ai_prompt import AIPrompt


def prompt() -> AIPrompt:
    return AIPrompt(
        system_instructions="system",
        user_payload='{"instrument":"NSE:CASH:RELIANCE"}',
        prompt_version="ai-004-v1",
    )


class FakeAdapter:
    def __init__(self, response: AIModelResponse) -> None:
        self.response = response
        self.received: AIPrompt | None = None

    def complete(self, value: AIPrompt) -> AIModelResponse:
        self.received = value
        return self.response


def test_gateway_passes_prompt_to_adapter_and_preserves_response() -> None:
    response = AIModelResponse(
        content='{"decision":"NO_TRADE"}',
        model_version="fake-v1",
        prompt_version="ai-004-v1",
    )
    adapter = FakeAdapter(response)

    result = AIModelGateway(adapter).complete(prompt())

    assert adapter.received == prompt()
    assert result == response


def test_empty_model_response_is_rejected() -> None:
    with pytest.raises(ValueError, match="model response content must not be empty"):
        AIModelResponse(content=" ", model_version="fake-v1", prompt_version="ai-004-v1")


def test_empty_model_version_is_rejected() -> None:
    with pytest.raises(ValueError, match="model_version must not be empty"):
        AIModelResponse(content="ok", model_version=" ", prompt_version="ai-004-v1")


def test_mismatched_prompt_version_is_rejected() -> None:
    adapter = FakeAdapter(
        AIModelResponse(
            content="opaque output",
            model_version="fake-v1",
            prompt_version="other-prompt-v1",
        )
    )

    with pytest.raises(ValueError, match="prompt_version must match prompt"):
        AIModelGateway(adapter).complete(prompt())


def test_model_output_is_not_interpreted() -> None:
    content = "BUY this looks convincing, but it remains untrusted text"
    response = AIModelResponse(
        content=content,
        model_version="fake-v1",
        prompt_version="ai-004-v1",
    )

    assert AIModelGateway(FakeAdapter(response)).complete(prompt()).content == content
