import json
from typing import Any

from langchain.tools import BaseTool, tool
from langchain_core.documents import Document
from qdrant_client import models

from app.services.vectorstore.client import get_vector_store

RETRIEVE_TOOL_NAME = "retrieve_context"

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


def build_notebook_filter(
    selected_chapters: list[dict[str, Any]],
) -> models.Filter | None:
    """Build a Qdrant filter limited to the notebook's selected chapters."""
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


def format_documents(documents: list[Document]) -> str:
    """Serialize retrieved documents into prompt-ready context blocks."""
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


def build_retrieve_tool(
    *,
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> BaseTool:
    """Create the notebook-scoped retrieve_context tool."""
    notebook_filter = build_notebook_filter(selected_chapters)

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
        return format_documents(documents)

    return retrieve_context
