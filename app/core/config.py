from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM / embeddings
    openai_api_key: str = Field(default="sk-dummy", alias="OPENAI_API_KEY")
    dense_model: str = "text-embedding-3-small"
    dense_vector_size: int = 1536
    embed_batch_size: int = 100

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    collection_name: str = "ncert_content"

    # Sparse retrieval
    sparse_model: str = "Qdrant/bm25"

    # App
    api_key: str | None = Field(default=None, alias="API_KEY")
    extracted_data_dir: Path = PROJECT_ROOT / "extracted_data"

    # NCERT book_code -> subject/grade
    ncert_book_config: dict[str, dict[str, str | int]] = {
        "jemh1": {"subject": "Mathematics", "grade": 10},
        "jesc1": {"subject": "Science", "grade": 10},
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
