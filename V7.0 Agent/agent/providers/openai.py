"""
OpenAI LLM provider.
Uses the official openai Python SDK with native function calling.
"""
from __future__ import annotations

import logging
from typing import Iterator

from openai import OpenAI

from agent.providers.base import BaseLLMProvider
from agent.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None):
        self._model = model or settings.openai.model
        self._client = OpenAI(
            api_key=api_key or settings.openai.api_key,
            base_url=base_url or settings.openai.base_url,
        )

    @property
    def model_name(self) -> str:
        return self._model

    def load_model(self) -> None:
        """No-op for cloud APIs."""
        logger.info("OpenAI provider ready (model: %s)", self._model)

    def unload_model(self) -> None:
        """No-op for cloud APIs."""
        pass

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Chat completion with optional tool calling.
        Returns {"content": str|None, "tool_calls": list|None}
        """
        kwargs = {
            "model": self._model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls = None
        if message.tool_calls:
            import json
            tool_calls = [
                {
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                    "id": tc.id,
                }
                for tc in message.tool_calls
            ]

        return {
            "content": message.content,
            "tool_calls": tool_calls,
            "raw_message": message,
        }

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """Stream a plain text response."""
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
