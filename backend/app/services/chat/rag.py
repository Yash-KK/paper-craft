import json
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from qdrant_client import models

from app.core.config import settings
from app.db.models.chat import ChatMessage, ChatMessageRole
from app.services.vectorstore.client import get_vector_store

RAG_CHAT_INSTRUCTIONS = """\
You are a subject-matter assistant for a teacher. They will ask you standalone questions - to
understand a concept, get an explanation, or solve a specific problem. There is no paper-
generation intent here; just answer what's asked.

WHAT YOU HAVE
Retrieved chunks from the teacher's own content library (textbook theory, worked examples,
exercises, notes - whatever's indexed), tagged with metadata like subject/grade/chapter where
available. The content may span any grade level, subject, or curriculum - don't assume a
specific one unless the retrieved chunks or the question itself make it clear.

HOW TO ANSWER
- Ground your answer in the retrieved chunks first - use their terminology, method, and
  notation, since that's what matches how the teacher's own material presents the topic.
- If the chunks only partially cover the question (e.g. they explain the concept but the
  teacher asked about an edge case, or asked to solve a problem not in the excerpt), fill the
  gap with your own knowledge - just don't contradict the source material or introduce a
  different method/convention than the one the retrieved content uses for this topic.
- If nothing retrieved is actually relevant, say so and answer from your own knowledge instead
  of forcing a connection to unrelated chunks.
- If retrieved chunks are ambiguous about grade level or method (e.g. a concept taught
  differently across grades/boards), briefly note that rather than silently picking one.

FOR CONCEPT QUESTIONS
Explain clearly and directly, pitched at the level implied by the retrieved content or the
teacher's phrasing. Use the source's own definitions/theorems where possible. A short example
helps more than a long definition - include one if the chunks have one, or make up a simple one
if not.

FOR PROBLEM-SOLVING QUESTIONS
Show the full step-by-step solution, not just the final answer - the teacher likely wants to
check the method or use it for teaching. Match the method/convention the retrieved content uses
for this type of problem unless asked for an alternative approach.

CONFIDENCE
Always give your full answer/findings - never withhold or vaguely dodge a question because
you're unsure. But if you're not confident it's correct (a tricky computation, a thin or
ambiguous source chunk, a topic you're reconstructing mostly from your own knowledge rather
than the retrieved content), say so explicitly: present what you found/worked out, then add a
clear flag such as "Worth double-checking this one" or "I'm not fully certain about this step"
- so the teacher knows to verify before using it, rather than assuming it's textbook-verified.

STYLE
Talk to the teacher as a peer, not a student - be direct, skip motivational framing, skip
"Great question!"-style filler. Keep answers as short as the question allows; expand only when
the question is genuinely open-ended or asks for depth.
"""

CONTEXT_METADATA_KEYS = (
    "book_code",
    "subject",
    "grade",
    "chapter_number",
    "chapter_name",
    "page_number",
    "chunk_id",
    "content_types",
)

RETRIEVE_TOOL_NAME = "retrieve_context"
TOOL_OUTPUT_PREVIEW_CHARS = 200


@lru_cache
def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_oss_model,
        api_key=settings.together_api_key,
        base_url=settings.together_base_url,
    )


def _build_notebook_filter(
    selected_chapters: list[dict[str, Any]],
) -> models.Filter | None:
    chapter_filters: list[models.Filter] = []
    for chapter in selected_chapters:
        book_code = chapter.get("book_code")
        chapter_number = chapter.get("chapter_number")
        if not book_code or chapter_number is None:
            continue
        chapter_filters.append(
            models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.book_code",
                        match=models.MatchValue(value=book_code),
                    ),
                    models.FieldCondition(
                        key="metadata.chapter_number",
                        match=models.MatchValue(value=chapter_number),
                    ),
                ]
            )
        )

    return models.Filter(should=chapter_filters) if chapter_filters else None


def _format_documents(documents: list[Any]) -> str:
    blocks: list[str] = []
    for document in documents:
        metadata = {
            key: document.metadata[key]
            for key in CONTEXT_METADATA_KEYS
            if key in document.metadata
        }
        blocks.append(
            f"metadata: {json.dumps(metadata, ensure_ascii=False)}\n"
            f"page_content:\n{document.page_content}"
        )
    return "\n\n------\n\n".join(blocks) if blocks else "No relevant passages found."


def _to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    history: list[BaseMessage] = []
    for message in messages:
        if message.role == ChatMessageRole.USER:
            history.append(HumanMessage(content=message.content))
        elif message.role == ChatMessageRole.ASSISTANT:
            history.append(AIMessage(content=message.content))
    return history


def _serialize_tool_input(raw: Any) -> str:
    if isinstance(raw, dict):
        if "query" in raw:
            return str(raw["query"])
        return json.dumps(raw, ensure_ascii=False)
    return str(raw)


def _serialize_tool_output(raw: Any) -> str:
    if hasattr(raw, "content"):
        raw = raw.content
    text = str(raw)
    if len(text) <= TOOL_OUTPUT_PREVIEW_CHARS:
        return text
    return text[:TOOL_OUTPUT_PREVIEW_CHARS] + "…"


def build_retrieve_tool(
    *,
    selected_chapters: list[dict[str, Any]],
    top_k: int,
):
    notebook_filter = _build_notebook_filter(selected_chapters)

    @tool(RETRIEVE_TOOL_NAME)
    async def retrieve_context(query: str) -> str:
        """Retrieve relevant passages from this notebook's selected chapters."""
        search_kwargs: dict[str, Any] = {"k": top_k}
        if notebook_filter is not None:
            search_kwargs["filter"] = notebook_filter

        retriever = get_vector_store().as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs,
        )
        documents = await retriever.ainvoke(query)
        return _format_documents(documents)

    return retrieve_context


def create_notebook_agent(
    *,
    selected_chapters: list[dict[str, Any]],
    top_k: int,
):
    retrieve_tool = build_retrieve_tool(
        selected_chapters=selected_chapters,
        top_k=top_k,
    )
    return create_agent(
        model=get_chat_model(),
        tools=[retrieve_tool],
        system_prompt=RAG_CHAT_INSTRUCTIONS,
    )


async def stream_notebook_chat(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> AsyncIterator[dict[str, Any]]:
    """Stream chat events the same way as deepagent-research."""
    tool_calls: list[dict[str, Any]] = []
    answer_parts: list[str] = []

    yield {"type": "thinking"}

    try:
        agent = create_notebook_agent(
            selected_chapters=selected_chapters,
            top_k=top_k,
        )
        messages = _to_langchain_history(history) + [
            HumanMessage(content=question)
        ]

        async for event in agent.astream_events(
            {"messages": messages},
            version="v2",
        ):
            kind = event["event"]

            if kind == "on_tool_start":
                tool_name = event.get("name", "")
                if tool_name != RETRIEVE_TOOL_NAME:
                    continue
                tool_input = _serialize_tool_input(
                    event.get("data", {}).get("input", {})
                )
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
                if tool_name != RETRIEVE_TOOL_NAME:
                    continue
                tool_output = _serialize_tool_output(
                    event.get("data", {}).get("output", "")
                )
                for tool_call in reversed(tool_calls):
                    if tool_call["tool"] == tool_name and tool_call["output"] is None:
                        tool_call["output"] = tool_output
                        break
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": tool_output,
                }

            elif kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if not chunk:
                    continue

                content = getattr(chunk, "content", "")

                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if text:
                                answer_parts.append(text)
                                yield {"type": "token", "content": text}
                elif isinstance(content, str) and content:
                    answer_parts.append(content)
                    yield {"type": "token", "content": content}

        yield {
            "type": "complete",
            "answer": "".join(answer_parts).strip(),
            "tool_calls": tool_calls,
        }
    except Exception as exc:
        yield {"type": "error", "message": str(exc)}
