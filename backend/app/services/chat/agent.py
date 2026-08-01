from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.services.chat.llm import get_chat_model
from app.services.chat.prompts import build_system_prompt
from app.services.chat.tools import (
    RETRIEVAL_SOURCE_ORDER,
    NotebookContext,
    format_retrieval_context,
    run_retrieval_sources,
)


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    return [
        HumanMessage(content=m.content)
        if m.role == ChatMessageRole.USER
        else AIMessage(content=m.content)
        for m in messages
        if m.role in (ChatMessageRole.USER, ChatMessageRole.ASSISTANT)
    ]


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    board: str | None = None,
    top_k: int,
    enabled_tools: frozenset[str] = frozenset(),
) -> AsyncIterator[dict[str, str]]:
    """Yield SSE events: token / tool_start / tool_end / done / error.

    When retrieval sources are enabled they all run concurrently, then the
    model is called once with the merged context.
    """
    messages = to_langchain_history(history[-5:]) + [HumanMessage(content=question)]

    if not enabled_tools:
        async for event in _stream_answer(messages, frozenset()):
            yield event
        return

    names = [name for name in RETRIEVAL_SOURCE_ORDER if name in enabled_tools]
    for name in names:
        yield {"event": "tool_start", "data": name}

    context = NotebookContext(
        selected_chapters=selected_chapters,
        board=board,
        top_k=top_k,
    )
    results = await run_retrieval_sources(
        query=question,
        enabled=enabled_tools,
        context=context,
    )

    for name, _ in results:
        yield {"event": "tool_end", "data": name}

    context_block = format_retrieval_context(results)
    grounded = list(messages)
    if context_block:
        grounded.append(
            HumanMessage(
                content=(
                    "Retrieved context (use when relevant; do not invent "
                    "citations beyond what appears here):\n\n"
                    f"{context_block}"
                )
            )
        )

    async for event in _stream_answer(grounded, enabled_tools):
        yield event


async def _stream_answer(
    messages: list[BaseMessage],
    enabled_sources: frozenset[str],
) -> AsyncIterator[dict[str, str]]:
    answer_parts: list[str] = []
    prompt = [SystemMessage(content=build_system_prompt(enabled_sources)), *messages]
    async for chunk in get_chat_model().astream(prompt):
        text = chunk.content if isinstance(chunk.content, str) else ""
        if text:
            answer_parts.append(text)
            yield {"event": "token", "data": text}
    yield {"event": "done", "data": "".join(answer_parts).strip()}
