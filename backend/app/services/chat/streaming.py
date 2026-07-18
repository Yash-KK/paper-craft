# chat/streaming.py
import json
from typing import Any

TOOL_OUTPUT_PREVIEW_CHARS = 200


def sse_event(payload: dict[str, Any]) -> dict[str, str]:
    """Wrap a payload for EventSourceResponse (it handles the wire format)."""
    return {"data": json.dumps(payload, default=str)}


def extract_text(msg: Any) -> str:
    """Pull only visible answer text from a message, dropping thinking/reasoning blocks."""
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def serialize_tool_input(raw: Any) -> str:
    """Turn tool input into a readable string for the UI."""
    if isinstance(raw, dict):
        return str(raw.get("query", json.dumps(raw, ensure_ascii=False)))
    return str(raw)


def serialize_tool_output(raw: Any) -> str:
    """Summarise tool output into a short UI-friendly snippet."""
    text = str(getattr(raw, "content", raw))
    return text if len(text) <= TOOL_OUTPUT_PREVIEW_CHARS else text[:TOOL_OUTPUT_PREVIEW_CHARS] + "…"