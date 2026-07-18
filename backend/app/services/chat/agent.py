# chat/agent.py
import asyncio
from collections.abc import AsyncIterator
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.prompts.rag import RAG_CHAT_INSTRUCTIONS
from app.services.chat.llm import get_chat_model
from app.services.chat.rag import RETRIEVE_TOOL_NAME, build_retrieve_tool
from app.services.chat.streaming import serialize_tool_input, serialize_tool_output
from app.services.chat.tools import WEB_SEARCH_TOOL_NAME, build_web_search_tool

STREAMED_TOOL_NAMES = {RETRIEVE_TOOL_NAME, WEB_SEARCH_TOOL_NAME}
_DONE = object()


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    """Convert persisted chat messages into LangChain history."""
    history: list[BaseMessage] = []
    for message in messages:
        if message.role == ChatMessageRole.USER:
            history.append(HumanMessage(content=message.content))
        elif message.role == ChatMessageRole.ASSISTANT:
            history.append(AIMessage(content=message.content))
    return history


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
) -> AsyncIterator[dict[str, Any]]:
    """Stream normalized chat events from the notebook agent."""
    yield {"type": "thinking"}

    queue: asyncio.Queue[dict[str, Any] | object] = asyncio.Queue()
    tool_calls: list[dict[str, Any]] = []
    answer_parts: list[str] = []

    async def consume_text(stream) -> None:
        async for message in stream.messages:
            async for delta in message.text:
                answer_parts.append(delta)
                await queue.put({"type": "token", "content": delta})

    async def consume_tools(stream) -> None:
        async for call in stream.tool_calls:
            if call.tool_name not in STREAMED_TOOL_NAMES:
                continue
            if call.tool_name == WEB_SEARCH_TOOL_NAME and not call.input.get("query"):
                continue

            tool_input = serialize_tool_input(call.input)
            record = {"tool": call.tool_name, "input": tool_input, "output": None, "status": "done"}
            tool_calls.append(record)
            await queue.put({"type": "tool_start", "tool": call.tool_name, "input": tool_input})

            output = serialize_tool_output(await call.output)
            record["output"] = output
            await queue.put({"type": "tool_end", "tool": call.tool_name, "output": output})

            if call.tool_name == WEB_SEARCH_TOOL_NAME and not answer_parts:
                answer_parts.append(output)
                await queue.put({"type": "token", "content": output})

    async def run() -> None:
        try:
            agent = create_notebook_agent(selected_chapters=selected_chapters, top_k=top_k)
            messages = to_langchain_history(history) + [HumanMessage(content=question)]
            stream = await agent.astream_events({"messages": messages}, version="v3")
            await asyncio.gather(consume_text(stream), consume_tools(stream))
        except Exception as exc:
            await queue.put({"type": "error", "message": str(exc)})
        finally:
            await queue.put(_DONE)

    task = asyncio.create_task(run())
    try:
        while (event := await queue.get()) is not _DONE:
            yield event
            if event["type"] == "error":
                return
        yield {"type": "complete", "answer": "".join(answer_parts).strip(), "tool_calls": tool_calls}
    finally:
        task.cancel()