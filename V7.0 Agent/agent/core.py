"""
Agent core — the main execution loop.

This is where the magic happens:
1. User message → LLM (with tool schemas)
2. LLM returns tool_calls? → Execute tools → Feed results back → Loop
3. LLM returns text? → Show to user

The recursive tool-calling loop (from V6.0) is preserved but
now works with ANY registered tool and ANY LLM provider.
"""
from __future__ import annotations

import logging
from typing import Callable

from agent.providers.base import BaseLLMProvider
from agent.tools.registry import ToolRegistry, get_registry
from agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Maximum recursive tool calls to prevent infinite loops
MAX_TOOL_ROUNDS = 10


class Agent:
    """
    The central Agent class.

    Wires together an LLM provider and a tool registry,
    manages conversation history, and runs the tool-calling loop.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        registry: ToolRegistry | None = None,
        system_prompt: str | None = None,
        max_history: int = 50,
    ):
        self.provider = provider
        self.registry = registry or get_registry()
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self.max_history = max_history
        self.messages: list[dict] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self._on_tool_call: Callable | None = None

    def on_tool_call(self, callback: Callable[[str, dict, str], None]) -> None:
        """
        Register a callback for tool call events.
        callback(tool_name, arguments, result)
        """
        self._on_tool_call = callback

    def chat(self, user_input: str) -> str:
        """
        Process a user message and return the assistant's final response.
        Handles the full tool-calling loop internally.
        """
        self.messages.append({"role": "user", "content": user_input})
        self._trim_history()

        tools = self.registry.schemas if len(self.registry) > 0 else None
        response_text = self._tool_loop(tools, rounds=0)

        if response_text:
            self.messages.append({"role": "assistant", "content": response_text})

        return response_text or ""

    def _tool_loop(self, tools: list[dict] | None, rounds: int) -> str | None:
        """
        Recursive tool-calling loop.

        If the LLM requests tool calls, execute them, append results
        to the conversation, and call the LLM again. Repeat until
        the LLM returns a text response or we hit MAX_TOOL_ROUNDS.
        """
        if rounds >= MAX_TOOL_ROUNDS:
            logger.warning("Max tool rounds (%d) reached", MAX_TOOL_ROUNDS)
            return "I've reached the maximum number of tool calls for this turn. Please provide further guidance."

        result = self.provider.chat(self.messages, tools=tools)

        tool_calls = result.get("tool_calls")
        if not tool_calls:
            # No tool calls — return the text response
            return result.get("content")

        # Append the assistant's tool-call message to history
        raw = result.get("raw_message")
        if raw:
            # For Ollama: raw_message is a dict
            if isinstance(raw, dict):
                self.messages.append(raw)
            else:
                # For OpenAI: raw_message is a ChatCompletionMessage object
                self.messages.append({
                    "role": "assistant",
                    "content": raw.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in (raw.tool_calls or [])
                    ],
                })

        # Execute each tool call and append results
        for tc in tool_calls:
            name = tc["name"]
            args = tc["arguments"]
            logger.info("Tool call: %s(%s)", name, args)

            tool_result = self.registry.execute(name, args)

            if self._on_tool_call:
                self._on_tool_call(name, args, tool_result)

            # Append tool result — format differs by provider
            tool_msg = {
                "role": "tool",
                "content": tool_result,
                "name": name,
            }
            # OpenAI requires tool_call_id
            if "id" in tc:
                tool_msg["tool_call_id"] = tc["id"]

            self.messages.append(tool_msg)

        # Recurse — let the LLM see the tool results and continue
        return self._tool_loop(tools, rounds + 1)

    def _trim_history(self) -> None:
        """
        Keep conversation history bounded.
        Always preserves the system message (index 0).
        Removes oldest messages when limit is exceeded.
        """
        if len(self.messages) <= self.max_history:
            return
        # Keep system prompt + last (max_history - 1) messages
        system = self.messages[0]
        self.messages = [system] + self.messages[-(self.max_history - 1):]
        logger.debug("History trimmed to %d messages", len(self.messages))

    def reset(self) -> None:
        """Clear conversation history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
