from qdrant_client import models

from app.core.config import settings
from app.services.vectorstore.client import get_qdrant_client


def _pool_key(
    subject: str,
    grade: int,
    chapter_number: int,
    content_types: list[str],
    book_code: str | None,
) -> tuple:
    return (subject.lower(), grade, chapter_number, tuple(content_types), book_code)


def get_chapter_pool(
    subject: str,
    grade: int,
    chapter_number: int,
    content_types: list[str],
    book_code: str | None = None,
    *,
    cache: dict[tuple, list[dict]],
    limit: int = 50,
) -> list[dict]:
    key = _pool_key(subject, grade, chapter_number, content_types, book_code)
    if key in cache:
        return cache[key]

    must = [
        models.FieldCondition(
            key="metadata.subject",
            match=models.MatchValue(value=subject.lower()),
        ),
        models.FieldCondition(
            key="metadata.grade",
            match=models.MatchValue(value=grade),
        ),
        models.FieldCondition(
            key="metadata.chapter_number",
            match=models.MatchValue(value=chapter_number),
        ),
        models.FieldCondition(
            key="metadata.content_type",
            match=models.MatchAny(any=content_types),
        ),
    ]
    if book_code:
        must.append(
            models.FieldCondition(
                key="metadata.book_code",
                match=models.MatchValue(value=book_code),
            )
        )

    records, _ = get_qdrant_client().scroll(
        collection_name=settings.collection_name,
        scroll_filter=models.Filter(must=must),
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )

    pool = [
        {
            "chunk_id": record.payload["metadata"]["chunk_id"],
            "text": record.payload["page_content"],
        }
        for record in records
        if record.payload and "metadata" in record.payload
    ]
    cache[key] = pool
    return pool


def pick_chunks(
    pool: list[dict],
    n: int,
    cursor: dict[tuple, int],
    key: tuple,
) -> list[dict]:
    if not pool:
        return []
    picked = []
    for _ in range(n):
        idx = cursor.get(key, 0) % len(pool)
        picked.append(pool[idx])
        cursor[key] = idx + 1
    return picked


def attach_context_node(state: dict) -> dict:
    """Attach 1–2 textbook chunks per slot. Cache pools only for this invoke."""
    cache: dict[tuple, list[dict]] = {}
    cursor: dict[tuple, int] = {}
    slots_with_context = []

    for slot in state["slots"]:
        content_types = slot.get("content_types") or ["theory", "example"]
        book_code = slot.get("book_code")
        key = _pool_key(
            state["subject"],
            state["grade"],
            slot["chapter_number"],
            content_types,
            book_code,
        )
        pool = get_chapter_pool(
            state["subject"],
            state["grade"],
            slot["chapter_number"],
            content_types,
            book_code,
            cache=cache,
        )
        # Prefer 2 chunks when theory is in the filter (longer / multi-part questions).
        n = 2 if "theory" in content_types else 1
        chunks = pick_chunks(pool, n, cursor, key)
        slots_with_context.append({**slot, "context_chunks": chunks})

    return {"slots": slots_with_context}
