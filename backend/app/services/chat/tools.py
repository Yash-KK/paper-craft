# chat/tools.py
import json
from dataclasses import dataclass
from typing import Any

from langchain.tools import ToolRuntime, tool
from langchain_tavily import TavilySearch
from qdrant_client import models

from app.core.config import settings
from app.services.vectorstore.client import get_vector_store

_METADATA_KEYS = (
    "book_code",
    "subject",
    "grade",
    "chapter_number",
    "chapter_name",
    "page_number",
    "chunk_id",
    "content_types",
)


@dataclass
class NotebookContext:
    """Per-turn notebook scope passed into agent.astream(context=...)."""

    selected_chapters: list[dict[str, Any]]
    top_k: int


@tool("retrieve_context")
async def retrieve_context(query: str, runtime: ToolRuntime[NotebookContext]) -> str:
    """Retrieve relevant passages from this notebook's selected chapters."""
    selected_chapters = runtime.context.selected_chapters
    top_k = runtime.context.top_k

    chapter_filters = [
        models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.book_code",
                    match=models.MatchValue(value=chapter["book_code"]),
                ),
                models.FieldCondition(
                    key="metadata.chapter_number",
                    match=models.MatchValue(value=chapter["chapter_number"]),
                ),
            ]
        )
        for chapter in selected_chapters
        if chapter.get("book_code") and chapter.get("chapter_number") is not None
    ]
    search_kwargs: dict[str, Any] = {"k": top_k}
    if chapter_filters:
        search_kwargs["filter"] = models.Filter(should=chapter_filters)

    docs = await get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    ).ainvoke(query)

    if not docs:
        return "No relevant passages found."

    blocks = []
    for doc in docs:
        meta = {k: doc.metadata[k] for k in _METADATA_KEYS if k in doc.metadata}
        blocks.append(
            f"metadata: {json.dumps(meta, ensure_ascii=False)}\n"
            f"page_content:\n{doc.page_content}"
        )
    return "\n\n------\n\n".join(blocks)


@tool(
    "web_search",
    description=(
        "Searches the web for current, factual, and up-to-date information. "
        "Use it for recent events, factual lookups, statistics, news, "
        "documentation, and information that may have changed. "
        "Input should be a concise, specific search query."
    ),
)
def web_search(query: str) -> Any:
    """Search the web using Tavily."""
    if settings.tavily_api_key is None:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    return TavilySearch(
        max_results=3,
        topic="general",
        search_depth="basic",
        include_answer=True,
        tavily_api_key=settings.tavily_api_key.get_secret_value(),
    ).invoke(query)


AGENT_TOOLS = [retrieve_context, web_search]
