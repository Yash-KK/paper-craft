# chat/tools.py
import json
from typing import Any

from langchain.tools import BaseTool, tool
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from qdrant_client import models

from app.core.config import settings
from app.services.vectorstore.client import get_vector_store

RETRIEVE_TOOL_NAME = "retrieve_context"
WEB_SEARCH_TOOL_NAME = "tavily_search"

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


def _notebook_filter(selected_chapters: list[dict[str, Any]]) -> models.Filter | None:
    chapter_filters: list[models.FieldCondition | models.Filter] = []
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


def _format_documents(documents: list[Document]) -> str:
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


def _format_search_result(result: Any) -> str:
    if not isinstance(result, dict):
        return str(result)

    answer = result.get("answer")
    if answer:
        return str(answer)

    snippets: list[str] = []
    for item in result.get("results", [])[:3]:
        if not isinstance(item, dict):
            continue
        title = item.get("title", "")
        content = str(item.get("content", ""))[:200]
        snippets.append(f"{title}: {content}".strip())
    return "\n".join(snippets) or "No web search results found."


def build_retrieve_tool(*, selected_chapters: list[dict[str, Any]], top_k: int) -> BaseTool:
    notebook_filter = _notebook_filter(selected_chapters)

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
        return _format_documents(await retriever.ainvoke(query))

    return retrieve_context


def build_web_search_tool() -> BaseTool:
    @tool(
        WEB_SEARCH_TOOL_NAME,
        return_direct=True,
        description=(
            "Searches the web for current, factual, and up-to-date information. "
            "Use it for recent events, factual lookups, statistics, news, "
            "documentation, and information that may have changed. "
            "Input should be a concise, specific search query."
        ),
    )
    async def web_search(query: str) -> Any:
        """Search the web using Tavily."""
        if settings.tavily_api_key is None:
            raise RuntimeError("TAVILY_API_KEY is not configured")

        search = TavilySearch(
            max_results=3,
            topic="general",
            search_depth="basic",
            include_answer=True,
            tavily_api_key=settings.tavily_api_key.get_secret_value(),
        )
        return _format_search_result(await search.ainvoke(query))

    return web_search


def build_agent_tools(*, selected_chapters: list[dict[str, Any]], top_k: int) -> list[BaseTool]:
    """Retriever + web search tools for the notebook chat agent."""
    return [
        build_retrieve_tool(selected_chapters=selected_chapters, top_k=top_k),
        build_web_search_tool(),
    ]
