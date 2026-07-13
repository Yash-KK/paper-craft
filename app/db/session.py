from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Async engine + session for FastAPI (asyncpg).
async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Sync engine + session for Celery workers / scripts (psycopg2).
sync_engine = create_engine(
    settings.database_sync_url,
    echo=False,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async session, rolling back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """Context manager for sync code (e.g. Celery tasks), rolling back on error."""
    with SyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
