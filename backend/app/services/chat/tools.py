from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from langchain_tavily import TavilySearch
from qdrant_client import models

from app.core.config import settings
from app.services.vectorstore.client import get_vector_store

_METADATA_KEYS = (
    "book_code",
    "board",
    "subject",
    "grade",
    "chapter_number",
    "chapter_name",
    "page_number",
    "chunk_id",
    "content_types",
)

RetrievalFn = Callable[["NotebookContext", str], Awaitable[str]]


@dataclass
class NotebookContext:
    """Per-turn notebook scope for retrieval."""

    selected_chapters: list[dict[str, Any]]
    board: str | None
    top_k: int


async def retrieve_context(context: NotebookContext, query: str) -> str:
    """Retrieve relevant passages from this notebook's selected chapters."""
    chapter_filters = []
    for chapter in context.selected_chapters:
        if not chapter.get("book_code") or chapter.get("chapter_number") is None:
            continue
        must = [
            models.FieldCondition(
                key="metadata.book_code",
                match=models.MatchValue(value=chapter["book_code"]),
            ),
            models.FieldCondition(
                key="metadata.chapter_number",
                match=models.MatchValue(value=chapter["chapter_number"]),
            ),
        ]
        if context.board:
            must.append(
                models.FieldCondition(
                    key="metadata.board",
                    match=models.MatchValue(value=context.board),
                )
            )
        chapter_filters.append(models.Filter(must=must))

    search_kwargs: dict[str, Any] = {"k": context.top_k}
    if chapter_filters:
        search_kwargs["filter"] = models.Filter(should=chapter_filters)

    docs = await (
        get_vector_store()
        .as_retriever(search_type="similarity", search_kwargs=search_kwargs)
        .ainvoke(query)
    )
    if not docs:
        return "No relevant passages found."

    return "\n\n------\n\n".join(
        f"metadata: {json.dumps({k: doc.metadata[k] for k in _METADATA_KEYS if k in doc.metadata}, ensure_ascii=False)}\n"
        f"page_content:\n{doc.page_content}"
        for doc in docs
    )


async def web_search(_context: NotebookContext, query: str) -> str:
    """Search the web using Tavily (sync client, run in a worker thread)."""
    if settings.tavily_api_key is None:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    result = await asyncio.to_thread(
        TavilySearch(
            max_results=5,
            topic="general",
            search_depth="advanced",
            include_answer=True,
            tavily_api_key=settings.tavily_api_key.get_secret_value(),
        ).invoke,
        query,
    )
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, indent=2)


# Stable order for UI + context blocks. Register new sources here.
RETRIEVAL_SOURCE_ORDER: tuple[str, ...] = ("retrieve_context", "web_search")

RETRIEVAL_SOURCES: dict[str, RetrievalFn] = {
    "retrieve_context": retrieve_context,
    "web_search": web_search,
}

RETRIEVAL_SOURCE_LABELS: dict[str, str] = {
    "retrieve_context": "Textbook",
    "web_search": "Web Search",
}


async def run_retrieval_sources(
    *,
    query: str,
    enabled: frozenset[str],
    context: NotebookContext,
) -> list[tuple[str, str]]:
    """Run every enabled source concurrently; return ``(source_name, result_text)``."""
    names = [name for name in RETRIEVAL_SOURCE_ORDER if name in enabled]
    raw = await asyncio.gather(
        *(RETRIEVAL_SOURCES[name](context, query) for name in names),
        return_exceptions=True,
    )
    return [
        (
            name,
            f"Retrieval failed: {value}"
            if isinstance(value, BaseException)
            else value,
        )
        for name, value in zip(names, raw, strict=True)
    ]


def format_retrieval_context(results: list[tuple[str, str]]) -> str:
    """Merge per-source results into one context block for the LLM."""
    return "\n\n".join(
        f"### {RETRIEVAL_SOURCE_LABELS.get(name, name)} ({name})\n{text.strip()}"
        for name, text in results
    )
