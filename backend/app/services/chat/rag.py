import json
from functools import lru_cache
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from qdrant_client import models

from app.core.config import settings
from app.db.models.chat import ChatMessage, ChatMessageRole
from app.services.vectorstore.client import get_vector_store

RAG_CHAT_INSTRUCTIONS = """\
You are a subject-matter assistant for a teacher. Answer the teacher's question using the
retrieved textbook context first.

- Match the terminology, notation, and method used by the retrieved material.
- If the context only partially answers the question, complete the answer using your own
  knowledge without contradicting the material.
- If the context is irrelevant, say that the notebook sources do not cover the question, then
  answer from your own knowledge.
- For problem-solving questions, show the complete method.
- Be direct and concise. Do not use motivational filler.
- Never invent a citation or claim that a source says something absent from the context.

Retrieved notebook context:
{context}
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


@lru_cache
def get_chat_model() -> ChatOpenAI:
    api_key = settings.chat_api_key or settings.openai_api_key
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=api_key,
        base_url=settings.chat_base_url,
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
    return "\n\n------\n\n".join(blocks)


def _to_langchain_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    history: list[BaseMessage] = []
    for message in messages:
        if message.role == ChatMessageRole.USER:
            history.append(HumanMessage(content=message.content))
        elif message.role == ChatMessageRole.ASSISTANT:
            history.append(AIMessage(content=message.content))
    return history


def _citation_from_document(document: Any) -> dict[str, Any]:
    metadata = document.metadata
    chunk_id = str(metadata.get("chunk_id") or metadata.get("_id") or "")
    return {
        "id": chunk_id,
        "title": metadata.get("chapter_name") or metadata.get("source_file") or "Source",
        "snippet": document.page_content[:300],
        "book_code": metadata.get("book_code"),
        "chapter_number": metadata.get("chapter_number"),
        "chapter_name": metadata.get("chapter_name"),
        "page_number": metadata.get("page_number"),
    }


async def generate_rag_response(
    *,
    question: str,
    history: list[ChatMessage],
    selected_chapters: list[dict[str, Any]],
    top_k: int,
) -> tuple[str, list[dict[str, Any]]]:
    search_kwargs: dict[str, Any] = {"k": top_k}
    notebook_filter = _build_notebook_filter(selected_chapters)
    if notebook_filter is not None:
        search_kwargs["filter"] = notebook_filter

    retriever = get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )
    documents = await retriever.ainvoke(question)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_CHAT_INSTRUCTIONS),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    chain = prompt | get_chat_model() | StrOutputParser()
    answer = await chain.ainvoke(
        {
            "context": _format_documents(documents),
            "history": _to_langchain_history(history),
            "question": question,
        }
    )

    citations = [_citation_from_document(document) for document in documents]
    return answer, citations
