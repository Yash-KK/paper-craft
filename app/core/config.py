import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    dense_model: str = Field(alias="DENSE_MODEL")
    qdrant_url: str = Field(alias="QDRANT_URL")
    collection_name: str = Field(alias="COLLECTION_NAME")
    sparse_model: str = Field(alias="SPARSE_MODEL")
    extracted_data_dir: Path = Field(alias="EXTRACTED_DATA_DIR")
    ncert_book_config: dict[str, dict[str, str | int]] = Field(alias="NCERT_BOOK_CONFIG")

    @field_validator("extracted_data_dir", mode="before")
    @classmethod
    def resolve_extracted_data_dir(cls, value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else PROJECT_ROOT / path

    @field_validator("ncert_book_config", mode="before")
    @classmethod
    def parse_ncert_book_config(cls, value: str | dict) -> dict:
        if isinstance(value, str):
            return json.loads(value)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
