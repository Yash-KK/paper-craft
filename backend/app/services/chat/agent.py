from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any, cast

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.services.chat.llm import get_chat_model
from app.services.chat.prompts import build_system_prompt
from app.services.chat.tools import NotebookContext, retrieve_context, web_search


def to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    return [
        HumanMessage(content=m.content)
        if m.role == ChatMessageRole.USER
        else AIMessage(content=m.content)
        for m in messages
        if m.role in (ChatMessageRole.USER, ChatMessageRole.ASSISTANT)
    ]


@lru_cache
def get_chat_agent(enable_web_search: bool = False) -> Any:
    tools = [retrieve_context, web_search] if enable_web_search else [retrieve_context]
    return create_agent(
        model=get_chat_model(),
        tools=tools,
        system_prompt=build_system_prompt(enable_web_search=enable_web_search),
        context_schema=NotebookContext,
    )


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
    enable_web_search: bool = False,
) -> AsyncIterator[dict[str, str]]:
    """Yield SSE events: token / tool_start / tool_end / done / error.

    Pre-tool model chatter is dropped — only the final answer is streamed.
    """
    answer_parts: list[str] = []
    stream_answer = True

    try:
        agent = get_chat_agent(enable_web_search)
        messages = to_langchain_history(history[-5:]) + [HumanMessage(content=question)]
        context = NotebookContext(selected_chapters=selected_chapters, top_k=top_k)

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
