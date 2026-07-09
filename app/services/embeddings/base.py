from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list:
        """Embed a batch of document/passage texts."""

    @abstractmethod
    def embed_query(self, text: str):
        """Embed a single query text."""
