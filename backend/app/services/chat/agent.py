from collections.abc import AsyncIterator
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.prompts.rag import RAG_CHAT_INSTRUCTIONS
from app.services.chat.llm import get_chat_model
from app.services.chat.rag import RETRIEVE_TOOL_NAME, build_retrieve_tool
from app.services.chat.streaming import (
    chunk_has_tool_calls,
    extract_stream_text,
    serialize_tool_input,
    serialize_tool_output,
)
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


def create_notebook_agent(
    *,
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> CompiledStateGraph:
    """Build a notebook-scoped ReAct agent with the retrieve_context tool."""
    retrieve_tool = build_retrieve_tool(
        selected_chapters=selected_chapters,
        top_k=top_k,
    )
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
) -> AsyncIterator[dict[str, Any]]:
    """Stream normalized chat events from the notebook agent."""
    tool_calls: list[dict[str, Any]] = []
    answer_parts: list[str] = []
    model_turn_calls_tool = False

    yield {"type": "thinking"}

    try:
        agent = create_notebook_agent(
            selected_chapters=selected_chapters,
            top_k=top_k,
        )
        messages = to_langchain_history(history) + [
            HumanMessage(content=question)
        ]

        async for event in agent.astream_events(
            {"messages": messages},
            version="v2",
        ):
            kind = event["event"]

            if kind == "on_chat_model_start":
                model_turn_calls_tool = False

            elif kind == "on_tool_start":
                tool_name = event.get("name", "")
                if tool_name not in STREAMED_TOOL_NAMES:
                    continue
                raw_input: Any = event.get("data", {}).get("input", {})
                if (
                    tool_name == WEB_SEARCH_TOOL_NAME
                    and (
                        not isinstance(raw_input, dict)
                        or not raw_input.get("query")
                    )
                ):
                    continue
                tool_input = serialize_tool_input(raw_input)
                tool_calls.append(
                    {
                        "tool": tool_name,
                        "input": tool_input,
                        "output": None,
                        "status": "done",
                    }
                )
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "input": tool_input,
                }

            elif kind == "on_tool_end":
                tool_name = event.get("name", "")
                if tool_name not in STREAMED_TOOL_NAMES:
                    continue
                raw_output = event.get("data", {}).get("output", "")
                if (
                    tool_name == WEB_SEARCH_TOOL_NAME
                    and not hasattr(raw_output, "content")
                ):
                    continue
                tool_output = serialize_tool_output(raw_output)
                for tool_call in reversed(tool_calls):
                    if tool_call["tool"] == tool_name and tool_call["output"] is None:
                        tool_call["output"] = tool_output
                        break
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": tool_output,
                }
                if tool_name == WEB_SEARCH_TOOL_NAME and not answer_parts:
                    answer_parts.append(tool_output)
                    yield {"type": "token", "content": tool_output}

            elif kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if not chunk:
                    continue
                if chunk_has_tool_calls(chunk):
                    model_turn_calls_tool = True
                    continue
                if model_turn_calls_tool:
                    continue
                for text in extract_stream_text(chunk):
                    if tool_calls and not answer_parts and text.strip().lower() in {
                        "final",
                        "assistant",
                    }:
                        continue
                    answer_parts.append(text)
                    yield {"type": "token", "content": text}

        yield {
            "type": "complete",
            "answer": "".join(answer_parts).strip(),
            "tool_calls": tool_calls,
        }
    except Exception as exc:
        yield {"type": "error", "message": str(exc)}
