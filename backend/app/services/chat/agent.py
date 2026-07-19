# chat/agent.py
from collections.abc import AsyncIterator
from typing import Any, cast

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.prompts.rag import RAG_CHAT_INSTRUCTIONS
from app.services.chat.llm import get_chat_model
from app.services.chat.tools import build_agent_tools


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    return [
        HumanMessage(content=m.content)
        if m.role == ChatMessageRole.USER
        else AIMessage(content=m.content)
        for m in messages
        if m.role in (ChatMessageRole.USER, ChatMessageRole.ASSISTANT)
    ]


def get_chat_agent(*, selected_chapters: list[dict[str, Any]], top_k: int) -> CompiledStateGraph:
    """Build a notebook-scoped ReAct agent with retrieve + web search tools."""
    return create_agent(
        model=get_chat_model(),
        tools=build_agent_tools(selected_chapters=selected_chapters, top_k=top_k),
        system_prompt=RAG_CHAT_INSTRUCTIONS,
    )


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> AsyncIterator[dict[str, str]]:
    """Yield SSE events: token / tool_start / tool_end / done / error."""
    answer_parts: list[str] = []

    try:
        agent = get_chat_agent(selected_chapters=selected_chapters, top_k=top_k)
        messages = to_langchain_history(history) + [HumanMessage(content=question)]

        async for mode, chunk in agent.astream(
            {"messages": messages}, stream_mode=["messages", "updates"]
        ):
            if mode == "messages":
                msg, _ = cast(tuple[Any, Any], chunk)
                if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                    text = msg.content if isinstance(msg.content, str) else ""
                    if text:
                        answer_parts.append(text)
                        yield {"event": "token", "data": text}

            elif mode == "updates":
                for node_output in cast(dict[str, Any], chunk).values():
                    for m in node_output.get("messages", []):
                        if isinstance(m, AIMessage) and m.tool_calls:
                            for tc in m.tool_calls:
                                yield {"event": "tool_start", "data": tc["name"]}
                        elif isinstance(m, ToolMessage) and m.name:
                            yield {"event": "tool_end", "data": m.name}

        yield {"event": "done", "data": "".join(answer_parts).strip()}
    except Exception as exc:
        yield {"event": "error", "data": str(exc)}
