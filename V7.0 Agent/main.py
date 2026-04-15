#!/usr/bin/env python3
"""
CLI entry point for V7.0 Agent.

Usage:
    python main.py                  # Default: Ollama provider
    python main.py --provider openai
    python main.py --model qwen2.5:14b
"""
from __future__ import annotations

import argparse
import logging
import sys

# Import tools so they get registered via @tool decorator
import agent.tools.terminal   # noqa: F401
import agent.tools.ssh        # noqa: F401
import agent.tools.search     # noqa: F401

from agent.core import Agent
from agent.providers.ollama import OllamaProvider
from agent.providers.openai import OpenAIProvider
from agent.tools.registry import get_registry
from agent.tools.ssh import close_ssh


def build_provider(provider_name: str, model: str | None = None):
    """Factory: create the appropriate LLM provider."""
    if provider_name == "ollama":
        return OllamaProvider(model=model)
    elif provider_name == "openai":
        return OpenAIProvider(model=model)
    else:
        print(f"Unknown provider: {provider_name}")
        sys.exit(1)


def print_tool_call(name: str, arguments: dict, result: str) -> None:
    """Callback to display tool execution in the terminal."""
    args_str = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
    print(f"\n  🔧 {name}({args_str})")
    # Show truncated result
    lines = result.strip().split("\n")
    if len(lines) > 15:
        for line in lines[:10]:
            print(f"  │ {line}")
        print(f"  │ ... ({len(lines) - 10} more lines)")
    else:
        for line in lines:
            print(f"  │ {line}")
    print()


def main():
    parser = argparse.ArgumentParser(description="V7.0 Agent — LLM Agent with tool calling")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama",
                        help="LLM provider (default: ollama)")
    parser.add_argument("--model", type=str, default=None,
                        help="Override model name")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    # Logging
    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Build provider
    provider = build_provider(args.provider, args.model)

    # Load model (relevant for Ollama)
    try:
        provider.load_model()
    except Exception as e:
        print(f"Failed to initialize {args.provider}: {e}")
        sys.exit(1)

    # Build agent
    registry = get_registry()
    agent = Agent(provider=provider, registry=registry)
    agent.on_tool_call(print_tool_call)

    # Print welcome
    print(f"\n{'='*50}")
    print(f"  Star Agent v7.0 — {provider.model_name}")
    print(f"  Provider: {args.provider}")
    print(f"  Tools: {', '.join(registry.tool_names) or 'none'}")
    print(f"{'='*50}")
    print("  Type 'quit' to exit, 'reset' to clear history\n")

    # Main loop
    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye", "再见", "拜拜"):
                break

            if user_input.lower() == "reset":
                agent.reset()
                print("  (conversation reset)\n")
                continue

            print("\nStar: ", end="", flush=True)
            response = agent.chat(user_input)
            if response:
                print(response)
            print()

    except KeyboardInterrupt:
        print("\n")

    # Cleanup
    close_ssh()
    try:
        provider.unload_model()
    except Exception:
        pass

    print("Goodbye! 👋")


if __name__ == "__main__":
    main()
