import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    dense_model: str = Field(alias="DENSE_MODEL")
    openai_oss_model: str = Field(alias="OPENAI_OSS_MODEL")
    together_api_key: SecretStr = Field(alias="TOGETHER_API_KEY")
    together_base_url: str = Field(alias="TOGETHER_BASE_URL")
    tavily_api_key: SecretStr | None = Field(default=None, alias="TAVILY_API_KEY")
    qdrant_url: str = Field(alias="QDRANT_URL")
    collection_name: str = Field(alias="COLLECTION_NAME")
    sparse_model: str = Field(alias="SPARSE_MODEL")
    extracted_data_dir: Path = Field(alias="EXTRACTED_DATA_DIR")
    ncert_book_config: dict[str, dict[str, str | int]] = Field(alias="NCERT_BOOK_CONFIG")

    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(alias="GOOGLE_REDIRECT_URI")
    allow_insecure_http: bool = Field(default=False, alias="ALLOW_INSECURE_HTTP")

    # Async engine for FastAPI (asyncpg); sync engine for Celery workers (psycopg2).
    async_database_url: str = Field(alias="ASYNC_DATABASE_URL")
    sync_database_url: str = Field(alias="SYNC_DATABASE_URL")

    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

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
