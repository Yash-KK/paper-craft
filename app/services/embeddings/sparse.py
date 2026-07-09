from fastembed import SparseTextEmbedding

from app.core.config import settings
from app.services.embeddings.base import BaseEmbedder


class BM25SparseEmbedder(BaseEmbedder):
    def __init__(self) -> None:
        self._model = SparseTextEmbedding(model_name=settings.sparse_model)

    def embed_documents(self, texts: list[str]):
        return list(self._model.passage_embed(texts))

    def embed_query(self, text: str):
        return next(self._model.query_embed(text))
