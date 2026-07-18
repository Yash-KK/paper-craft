# chat/agent.py
from collections.abc import AsyncIterator
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.prompts.rag import RAG_CHAT_INSTRUCTIONS
from app.services.chat.llm import get_chat_model
from app.services.chat.rag import RETRIEVE_TOOL_NAME, build_retrieve_tool
from app.services.chat.tools import WEB_SEARCH_TOOL_NAME, build_web_search_tool

STREAMED_TOOL_NAMES = {RETRIEVE_TOOL_NAME, WEB_SEARCH_TOOL_NAME}


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    """Convert persisted chat messages into LangChain history."""
    history: list[BaseMessage] = []
    for message in messages:
        if message.role == ChatMessageRole.USER:
            history.append(HumanMessage(content=message.content))
        elif message.role == ChatMessageRole.ASSISTANT:
            history.append(AIMessage(content=message.content))
    return history


def extract_text(msg: AIMessage) -> str:
    """Visible answer text only — skips thinking/reasoning content blocks."""
    if isinstance(msg.content, str):
        return msg.content
    return "".join(
        block.get("text", "")
        for block in msg.content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def create_notebook_agent(*, selected_chapters: list[dict[str, Any]], top_k: int) -> CompiledStateGraph:
    """Build a notebook-scoped ReAct agent with the retrieve_context tool."""
    retrieve_tool = build_retrieve_tool(selected_chapters=selected_chapters, top_k=top_k)
    return create_agent(
        model=get_chat_model(),
        tools=[retrieve_tool, build_web_search_tool()],
        system_prompt=RAG_CHAT_INSTRUCTIONS,
    )


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> AsyncIterator[dict[str, str]]:
    """Yield SSE-ready {event, data} dicts: token / tool_start / tool_end / done / error."""
    answer_parts: list[str] = []

    try:
        agent = create_notebook_agent(selected_chapters=selected_chapters, top_k=top_k)
        messages = to_langchain_history(history) + [HumanMessage(content=question)]

        async for mode, chunk in agent.astream(
            {"messages": messages}, stream_mode=["messages", "updates"]
        ):
            if mode == "messages":
                msg, _ = chunk
                if not isinstance(msg, AIMessage) or msg.tool_calls:
                    continue  # tool-deciding turn, no visible text yet
                text = extract_text(msg)
                if text:
                    answer_parts.append(text)
                    yield {"event": "token", "data": text}

            elif mode == "updates":
                for node_output in chunk.values():
                    for m in node_output.get("messages", []):
                        if isinstance(m, AIMessage) and m.tool_calls:
                            for tc in m.tool_calls:
                                if tc["name"] in STREAMED_TOOL_NAMES:
                                    yield {"event": "tool_start", "data": tc["name"]}
                        elif isinstance(m, ToolMessage) and m.name in STREAMED_TOOL_NAMES:
                            yield {"event": "tool_end", "data": m.name}

        yield {"event": "done", "data": "".join(answer_parts).strip()}
    except Exception as exc:
        yield {"event": "error", "data": str(exc)}