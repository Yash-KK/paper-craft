from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient

from app.core.config import settings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
    )


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=settings.collection_name,
        embedding=OpenAIEmbeddings(
            model=settings.dense_model,
            openai_api_key=settings.openai_api_key,
        ),
        sparse_embedding=FastEmbedSparse(model_name=settings.sparse_model),
        retrieval_mode=RetrievalMode.HYBRID,
    )
