"""Tool registry and the concrete tools the agent can call.

Each tool exposes a JSON schema (used to advertise it to the LLM) and a
callable. The registry converts tools to the provider's tool-definition
format and dispatches tool calls by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.config import get_settings
from app.db import get_stock, init_db
from app.weather import get_weather


@dataclass
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    func: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, schema: dict[str, Any]):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._tools[name] = Tool(name, description, schema, func)
            return func

        return decorator

    def definitions(self) -> list[dict[str, Any]]:
        """Return Anthropic-style tool definitions."""
        return [
            {"name": t.name, "description": t.description, "input_schema": t.schema}
            for t in self._tools.values()
        ]

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name].func(**arguments)


registry = ToolRegistry()


@registry.register(
    name="get_stock",
    description="Look up how many units of a product are in stock by its SKU.",
    schema={
        "type": "object",
        "properties": {"sku": {"type": "string", "description": "Product SKU, e.g. SKU-100"}},
        "required": ["sku"],
    },
)
def _tool_get_stock(sku: str) -> dict:
    settings = get_settings()
    init_db(settings.database_path)
    result = get_stock(settings.database_path, sku)
    if result is None:
        return {"error": f"No product with SKU {sku}"}
    return result


@registry.register(
    name="get_weather",
    description="Get the current weather for a city.",
    schema={
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name, e.g. Pune"}},
        "required": ["city"],
    },
)
def _tool_get_weather(city: str) -> dict:
    try:
        return get_weather(city)
    except ValueError as exc:
        return {"error": str(exc)}
