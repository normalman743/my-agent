"""
Ollama LLM provider.
Uses Ollama's native /api/chat endpoint with tool calling support.
"""
from __future__ import annotations

import json
import logging
from typing import Iterator

import requests

from agent.providers.base import BaseLLMProvider
from agent.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):

    def __init__(self, model: str | None = None, api_url: str | None = None):
        self._model = model or settings.ollama.model
        self._api_url = api_url or settings.ollama.api_url

    @property
    def model_name(self) -> str:
        return self._model

    def load_model(self) -> None:
        """Pre-load model into Ollama memory."""
        payload = {"model": self._model, "messages": [], "keep_alive": "5m"}
        try:
            resp = requests.post(self._api_url, json=payload, timeout=120)
            resp.raise_for_status()
            logger.info("Model %s loaded", self._model)
        except requests.RequestException as e:
            logger.error("Failed to load model %s: %s", self._model, e)
            raise

    def unload_model(self) -> None:
        """Release model from Ollama memory."""
        payload = {"model": self._model, "messages": [], "keep_alive": 0}
        try:
            requests.post(self._api_url, json=payload, timeout=30)
            logger.info("Model %s unloaded", self._model)
        except requests.RequestException:
            pass

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Non-streaming chat with optional tool calling.
        Returns {"content": str|None, "tool_calls": list|None}
        """
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(self._api_url, json=payload, timeout=120)
        resp.raise_for_status()
        message = resp.json().get("message", {})

        tool_calls_raw = message.get("tool_calls")
        tool_calls = None
        if tool_calls_raw:
            tool_calls = [
                {
                    "name": tc["function"]["name"],
                    "arguments": tc["function"].get("arguments", {}),
                }
                for tc in tool_calls_raw
            ]

        return {
            "content": message.get("content"),
            "tool_calls": tool_calls,
            "raw_message": message,  # keep for appending to history
        }

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """Stream a plain text response, yielding chunks."""
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
        }
        resp = requests.post(self._api_url, json=payload, stream=True, timeout=120)
        resp.raise_for_status()

        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done"):
                    break
