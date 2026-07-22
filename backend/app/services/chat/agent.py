from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any, cast

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.services.chat.llm import get_chat_model
from app.services.chat.prompts import build_system_prompt
from app.services.chat.tools import NotebookContext, retrieve_context, web_search

CHAT_TOOLS = {
    "retrieve_context": retrieve_context,
    "web_search": web_search,
}


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    return [
        HumanMessage(content=m.content)
        if m.role == ChatMessageRole.USER
        else AIMessage(content=m.content)
        for m in messages
        if m.role in (ChatMessageRole.USER, ChatMessageRole.ASSISTANT)
    ]


@wrap_model_call
def _force_enabled_tools(request, handler):
    """Require every selected tool before the final answer."""
    used = {m.name for m in request.messages if isinstance(m, ToolMessage) and m.name}
    pending = [t.name for t in request.tools if getattr(t, "name", None) not in used]
    if pending:
        return handler(request.override(tool_choice=pending[0]))
    return handler(request.override(tool_choice="none"))


@lru_cache
def get_chat_agent(enabled_tools: frozenset[str]) -> Any:
    tools = [CHAT_TOOLS[name] for name in ("retrieve_context", "web_search") if name in enabled_tools]
    return create_agent(
        model=get_chat_model(),
        tools=tools,
        system_prompt=build_system_prompt(enabled_tools),
        context_schema=NotebookContext,
        middleware=[_force_enabled_tools],
    )


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
    enabled_tools: frozenset[str] = frozenset(),
) -> AsyncIterator[dict[str, str]]:
    """Yield SSE events: token / tool_start / tool_end / done / error."""
    messages = to_langchain_history(history[-5:]) + [HumanMessage(content=question)]

    try:
        if not enabled_tools:
            async for event in _stream_direct(messages):
                yield event
            return

        agent = get_chat_agent(enabled_tools)
        context = NotebookContext(selected_chapters=selected_chapters, top_k=top_k)
        answer_parts: list[str] = []
        stream_answer = True

        async for mode, chunk in agent.astream(
            {"messages": messages},
            stream_mode=["messages", "updates"],
            context=context,
        ):
            if mode == "updates":
                for node_output in cast(dict[str, Any], chunk).values():
                    for m in node_output.get("messages", []):
                        if isinstance(m, AIMessage) and m.tool_calls:
                            stream_answer = False
                            answer_parts.clear()
                            for tc in m.tool_calls:
                                yield {"event": "tool_start", "data": tc["name"]}
                        elif isinstance(m, ToolMessage) and m.name:
                            yield {"event": "tool_end", "data": m.name}
                            stream_answer = True

            elif mode == "messages" and stream_answer:
                msg, _ = cast(tuple[Any, Any], chunk)
                if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                    text = msg.content if isinstance(msg.content, str) else ""
                    if text:
                        answer_parts.append(text)
                        yield {"event": "token", "data": text}

        yield {"event": "done", "data": "".join(answer_parts).strip()}
    except Exception as exc:
        yield {"event": "error", "data": str(exc)}


async def _stream_direct(messages: list[BaseMessage]) -> AsyncIterator[dict[str, str]]:
    answer_parts: list[str] = []
    prompt = [SystemMessage(content=build_system_prompt(frozenset())), *messages]
    async for chunk in get_chat_model().astream(prompt):
        text = chunk.content if isinstance(chunk.content, str) else ""
        if text:
            answer_parts.append(text)
            yield {"event": "token", "data": text}
    yield {"event": "done", "data": "".join(answer_parts).strip()}
