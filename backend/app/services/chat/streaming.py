import json
from typing import Any

TOOL_OUTPUT_PREVIEW_CHARS = 200

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def encode_sse(payload: dict[str, Any]) -> str:
    """Encode a JSON payload as a Server-Sent Event data line."""
    return f"data: {json.dumps(payload, default=str)}\n\n"


def serialize_tool_input(raw: Any) -> str:
    """Turn tool input into a readable string for the UI."""
    if isinstance(raw, dict):
        if "query" in raw:
            return str(raw["query"])
        return json.dumps(raw, ensure_ascii=False)
    return str(raw)


def serialize_tool_output(raw: Any) -> str:
    """Summarise tool output into a short UI-friendly snippet."""
    if hasattr(raw, "content"):
        raw = raw.content
    text = str(raw)
    if len(text) <= TOOL_OUTPUT_PREVIEW_CHARS:
        return text
    return text[:TOOL_OUTPUT_PREVIEW_CHARS] + "…"


def extract_stream_text(chunk: Any) -> list[str]:
    """Extract text fragments from a LangChain chat model stream chunk."""
    content = getattr(chunk, "content", "")
    if isinstance(content, str) and content:
        return [content]
    if isinstance(content, list):
        texts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if text:
                    texts.append(text)
        return texts
    return []


def chunk_has_tool_calls(chunk: Any) -> bool:
    """Return whether a model chunk is building a tool call."""
    return bool(
        getattr(chunk, "tool_call_chunks", None)
        or getattr(chunk, "tool_calls", None)
    )
