import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _swap_driver(url: str, target: str) -> str:
    """Rewrite any postgres URL scheme to the given `postgresql+driver://` target."""
    scheme, sep, rest = url.partition("://")
    return target + rest if sep else url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    dense_model: str = Field(alias="DENSE_MODEL")
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
    # `database_sync_url` is derived from `database_url` when not set explicitly
    # (see `default_sync_url`), so an empty string here means "not provided".
    database_url: str = Field(alias="DATABASE_URL")
    database_sync_url: str = Field(default="", alias="DATABASE_SYNC_URL")

    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_async_driver(cls, value: str) -> str:
        """Normalize the connection string to the asyncpg driver."""
        return _swap_driver(value, "postgresql+asyncpg://")

    @model_validator(mode="after")
    def default_sync_url(self) -> "Settings":
        """Derive the sync (psycopg2) URL from the async URL when not set explicitly."""
        source = self.database_sync_url or self.database_url
        self.database_sync_url = _swap_driver(source, "postgresql+psycopg2://")
        return self

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
