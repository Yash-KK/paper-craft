from openai import OpenAI

from app.core.config import settings
from app.services.embeddings.base import BaseEmbedder


class OpenAIDenseEmbedder(BaseEmbedder):
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        batch_size = settings.embed_batch_size
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = self._client.embeddings.create(
                model=settings.dense_model,
                input=batch,
            )
            vectors.extend([item.embedding for item in response.data])
        return vectors

    def embed_query(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model=settings.dense_model,
            input=[text],
        )
        return response.data[0].embedding
