"""
Abstract base class for LLM providers.

All providers must implement the same interface so the Agent core
doesn't care which LLM backend is being used.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class BaseLLMProvider(ABC):
    """Unified interface for all LLM providers."""

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Send a chat completion request.

        Args:
            messages: OpenAI-format message list [{role, content}, ...]
            tools: Optional list of tool schemas (JSON Schema format)

        Returns:
            dict with keys:
                - "content": str | None — assistant's text reply
                - "tool_calls": list[dict] | None — tool call requests
                    Each: {"name": str, "arguments": dict}
        """
        ...

    @abstractmethod
    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """
        Stream a plain chat response (no tool calling).
        Yields text chunks as they arrive.
        """
        ...

    @abstractmethod
    def load_model(self) -> None:
        """Pre-load model into memory (relevant for Ollama, no-op for cloud APIs)."""
        ...

    @abstractmethod
    def unload_model(self) -> None:
        """Release model from memory."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the current model identifier."""
        ...
