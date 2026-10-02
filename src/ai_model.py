"""Provider-independent model adapter boundary for AI-005."""

from dataclasses import dataclass
from typing import Protocol

from src.ai_prompt import AIPrompt


@dataclass(frozen=True)
class AIModelResponse:
    """Opaque model output plus the versions needed for auditability."""

    content: str
    model_version: str
    prompt_version: str

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("model response content must not be empty")
        if not self.model_version.strip():
            raise ValueError("model_version must not be empty")
        if not self.prompt_version.strip():
            raise ValueError("prompt_version must not be empty")


class AIModelAdapter(Protocol):
    """Transport-neutral contract implemented by a future model provider."""

    def complete(self, prompt: AIPrompt) -> AIModelResponse:
        """Return opaque model output for one deterministic prompt."""
        ...


class AIModelGateway:
    """Validate the model-adapter boundary without interpreting model output."""

    def __init__(self, adapter: AIModelAdapter) -> None:
        self._adapter = adapter

    def complete(self, prompt: AIPrompt) -> AIModelResponse:
        """Send one prompt through the adapter and validate its response metadata."""
        if not isinstance(prompt, AIPrompt):
            raise TypeError("prompt must be an AIPrompt")

        response = self._adapter.complete(prompt)
        if not isinstance(response, AIModelResponse):
            raise TypeError("model adapter must return AIModelResponse")
        if response.prompt_version != prompt.prompt_version:
            raise ValueError("model response prompt_version must match prompt")
        return response
