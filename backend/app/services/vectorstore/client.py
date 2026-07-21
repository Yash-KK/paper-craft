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
            model=settings.aic_dense_embedding_model,
            api_key=settings.aic_api_key,
            base_url=settings.aic_base_url,
        ),
        sparse_embedding=FastEmbedSparse(model_name=settings.sparse_embedding_model),
        retrieval_mode=RetrievalMode.HYBRID,
    )
