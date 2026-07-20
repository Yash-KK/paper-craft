"""Populate test env vars before application modules are imported."""

import os

_TEST_ENV = {
    "OPENAI_API_KEY": "test-openai-key",
    "DENSE_MODEL": "text-embedding-3-small",
    "AIC_META_8_MODEL": "openai/gpt-oss-120b",
    "AIC_API_KEY": "test-aic-key",
    "AIC_BASE_URL": "https://api.aicredits.in/v1",
    "TAVILY_API_KEY": "test-tavily-key",
    "QDRANT_URL": "http://localhost:6333",
    "COLLECTION_NAME": "test-collection",
    "SPARSE_MODEL": "Qdrant/bm25",
    "EXTRACTED_DATA_DIR": "extracted_data",
    "NCERT_BOOK_CONFIG": "{}",
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "GOOGLE_REDIRECT_URI": "http://localhost:8000/auth/callback",
    "ASYNC_DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/test",
    "SYNC_DATABASE_URL": "postgresql+psycopg2://postgres:password@localhost:5432/test",
    "SECRET_KEY": "test-secret-key",
}

for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)
