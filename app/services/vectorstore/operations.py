import uuid
from typing import Any

from qdrant_client import QdrantClient, models

from app.core.config import settings


def ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(settings.collection_name):
        return
    client.create_collection(
        collection_name=settings.collection_name,
        vectors_config={
            "dense": models.VectorParams(
                size=settings.dense_vector_size,
                distance=models.Distance.COSINE,
            ),
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF),
        },
    )


def build_point(
    chunk: dict[str, Any],
    dense_vector: list[float],
    sparse_vector,
) -> models.PointStruct:
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))
    payload = {
        "page_content": chunk["page_content"],
        "chunk_id": chunk["chunk_id"],
        **chunk["metadata"],
    }
    return models.PointStruct(
        id=point_id,
        vector={
            "dense": dense_vector,
            "bm25": models.SparseVector(
                indices=sparse_vector.indices.tolist(),
                values=sparse_vector.values.tolist(),
            ),
        },
        payload=payload,
    )


def upsert_points(client: QdrantClient, points: list[models.PointStruct]) -> None:
    client.upsert(collection_name=settings.collection_name, points=points)
