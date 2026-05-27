"""Claude wrapper with JSON output parsing and a keyless mock fallback.

When ANTHROPIC_API_KEY is unset, every call returns deterministic structured
mock data so the full platform loop (and tests) runs without credentials.
"""
import json
import re
from typing import Any

from .config import settings

_SYSTEM = (
    "You are the engine of a Digital Employee Platform. You design, train, and "
    "evaluate digital employees. Always reply with a single valid JSON object "
    "matching the requested schema and nothing else."
)


def is_live() -> bool:
    return bool(settings.anthropic_api_key)


def _extract_json(text: str) -> Any:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def complete_json(prompt: str, mock: Any) -> Any:
    """Run a JSON-returning Claude completion, or return `mock` when keyless."""
    if not is_live():
        return mock
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return _extract_json(text)
    except Exception:
        # Never let an LLM failure break the platform loop.
        return mock
