"""Test bootstrap and shared fixtures."""

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

import tests.bootstrap_env  # noqa: F401  # must load before app imports
from app.api.deps import get_current_user, get_db
from app.db.models.user import AuthProvider, User, UserRole
from app.main import app


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def mock_user(user_id: UUID) -> User:
    return User(
        id=user_id,
        email="teacher@example.com",
        auth_provider=AuthProvider.GOOGLE,
        auth_provider_id="google-123",
        email_verified=True,
        full_name="Test Teacher",
        role=UserRole.TEACHER,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.get = AsyncMock(return_value=None)
    db.delete = AsyncMock()
    db.execute = AsyncMock()
    db.scalar = AsyncMock(return_value=None)
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def client(mock_user: User, mock_db: AsyncMock) -> Generator[TestClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db

    async def override_get_current_user() -> User:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def make_catalog_chapter(
    chapter_number: int,
    chapter_name: str,
    *,
    is_available: bool = True,
) -> MagicMock:
    chapter = MagicMock()
    chapter.board = "CBSE"
    chapter.book_code = "jemh1"
    chapter.chapter_number = chapter_number
    chapter.chapter_name = chapter_name
    chapter.is_available = is_available
    return chapter


def mock_execute_result(rows: list[MagicMock]) -> MagicMock:
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    result.scalar_one_or_none.return_value = rows[0] if len(rows) == 1 else None
    return result
