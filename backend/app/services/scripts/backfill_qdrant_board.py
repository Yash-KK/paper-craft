"""Backfill metadata.board=CBSE on existing Qdrant points that lack it."""

from app.core.config import settings
from app.services.vectorstore.client import get_qdrant_client


def backfill_qdrant_board(board: str = "CBSE") -> None:
    client = get_qdrant_client()
    collection = settings.collection_name
    updated = 0
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        if not points:
            break

        for point in points:
            payload = dict(point.payload or {})
            metadata = dict(payload.get("metadata") or {})
            if metadata.get("board"):
                continue
            metadata["board"] = board
            payload["metadata"] = metadata
            client.set_payload(
                collection_name=collection,
                payload=payload,
                points=[point.id],
            )
            updated += 1

        if offset is None:
            break

    print(f"Backfilled board={board!r} on {updated} points in {collection}")


if __name__ == "__main__":
    backfill_qdrant_board()
