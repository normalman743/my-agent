"""
Tool Registry — the core engineering highlight of this project.

Tools are registered via the @tool decorator, which:
1. Inspects the function signature (type hints + defaults)
2. Auto-generates the JSON Schema for LLM tool calling
3. Stores the callable for execution when the LLM requests it

Usage:
    @tool(description="Execute a shell command")
    def terminal(command: str, sudo: bool = False, timeout: int = 60) -> str:
        ...

The registry then provides:
    - registry.schemas  → list of JSON tool schemas for the LLM
    - registry.execute("terminal", {"command": "ls"})  → runs the function
"""
from __future__ import annotations

import inspect
import logging
from typing import Callable, Any, get_type_hints

logger = logging.getLogger(__name__)

# Python type → JSON Schema type mapping
_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolRegistry:
    """Central registry for all agent tools."""

    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, dict] = {}

    def register(self, func: Callable, description: str) -> None:
        """Register a function as a tool with auto-generated schema."""
        name = func.__name__
        schema = self._build_schema(func, description)
        self._tools[name] = func
        self._schemas[name] = schema
        logger.debug("Registered tool: %s", name)

    def _build_schema(self, func: Callable, description: str) -> dict:
        """Inspect function signature and build JSON Schema for LLM."""
        sig = inspect.signature(func)
        hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Determine JSON type
            py_type = hints.get(param_name, str)
            json_type = _TYPE_MAP.get(py_type, "string")

            prop: dict[str, Any] = {"type": json_type}

            # Extract description from docstring if available
            prop["description"] = f"Parameter: {param_name}"

            # Handle default values
            if param.default is not inspect.Parameter.empty:
                prop["default"] = param.default
            else:
                required.append(param_name)

            properties[param_name] = prop

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @property
    def schemas(self) -> list[dict]:
        """Return all tool schemas for passing to LLM."""
        return list(self._schemas.values())

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def execute(self, name: str, arguments: dict) -> str:
        """Execute a registered tool by name. Returns string result."""
        if name not in self._tools:
            return f"Error: unknown tool '{name}'"
        try:
            # Coerce argument types — LLMs often return strings for int/bool params
            coerced = self._coerce_args(name, arguments)
            result = self._tools[name](**coerced)
            return str(result) if result is not None else ""
        except Exception as e:
            logger.error("Tool '%s' failed: %s", name, e)
            return f"Error executing {name}: {e}"

    def _coerce_args(self, name: str, arguments: dict) -> dict:
        """Coerce string arguments to their declared types (int, bool, etc.)."""
        schema = self._schemas.get(name, {})
        props = schema.get("function", {}).get("parameters", {}).get("properties", {})
        coerced = {}
        for key, value in arguments.items():
            expected_type = props.get(key, {}).get("type")
            if isinstance(value, str):
                if expected_type == "integer":
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif expected_type == "number":
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                elif expected_type == "boolean":
                    value = value.lower() in ("true", "1", "yes")
            coerced[key] = value
        return coerced

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)


# Global registry instance
_registry = ToolRegistry()


def tool(description: str) -> Callable:
    """
    Decorator to register a function as an agent tool.

    @tool(description="Execute a shell command")
    def terminal(command: str, sudo: bool = False) -> str:
        ...
    """
    def decorator(func: Callable) -> Callable:
        _registry.register(func, description)
        return func
    return decorator


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _registry
