from functools import lru_cache

from openai import OpenAI
from qdrant_client import QdrantClient

from app.core.config import settings
from app.services.embeddings.openai import OpenAIDenseEmbedder
from app.services.embeddings.sparse import BM25SparseEmbedder
from app.services.llm.generator import ResponseGenerator
from app.services.vectorstore.client import get_qdrant_client


@lru_cache
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


def get_dense_embedder() -> OpenAIDenseEmbedder:
    return OpenAIDenseEmbedder()


def get_sparse_embedder() -> BM25SparseEmbedder:
    return BM25SparseEmbedder()


def get_response_generator() -> ResponseGenerator:
    return ResponseGenerator()


def get_qdrant() -> QdrantClient:
    return get_qdrant_client()
