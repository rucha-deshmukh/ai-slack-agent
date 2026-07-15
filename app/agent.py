"""The LLM tool-use loop.

Given a user message, the model may ask to call one or more tools. We execute
them, return the results, and let the model produce a final natural-language
answer. The loop is bounded to avoid runaway tool calling.
"""

from __future__ import annotations

import json
import logging

from app.config import get_settings
from app.tools import registry

logger = logging.getLogger(__name__)

MAX_TURNS = 5
SYSTEM_PROMPT = (
    "You are a helpful assistant in a Slack workspace. Use the available tools "
    "when you need live data (stock levels, weather). Keep replies concise and "
    "friendly."
)


def run_agent(user_message: str) -> str:
    """Run the tool-use loop and return the assistant's final text reply."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return _offline_fallback(user_message)

    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key, timeout=30.0)
    messages: list[dict] = [{"role": "user", "content": user_message}]

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=settings.chat_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=registry.definitions(),
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            logger.info("tool_call name=%s input=%s", block.name, block.input)
            try:
                result = registry.call(block.name, dict(block.input))
            except Exception as exc:  # surface tool errors back to the model
                result = {"error": str(exc)}
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "Sorry, I couldn't complete that request."


def _offline_fallback(user_message: str) -> str:
    """Deterministic reply used when no API key is configured (dev/tests).

    Performs naive keyword routing so the tool layer can be exercised without
    a live model.
    """
    lower = user_message.lower()
    if "stock" in lower or "sku-" in lower:
        import re

        match = re.search(r"sku-\d+", lower)
        if match:
            result = registry.call("get_stock", {"sku": match.group().upper()})
            return f"Stock info: {result}"
    if "weather" in lower:
        for city in ("pune", "mumbai", "london", "new york", "san francisco"):
            if city in lower:
                result = registry.call("get_weather", {"city": city})
                return f"Weather: {result}"
    return "I need an ANTHROPIC_API_KEY to answer general questions."
