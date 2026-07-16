from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse

from app.api.deps import get_db, get_google_sso
from app.core.config import settings
from app.db.models.user import User
from app.main import app
from tests.conftest import mock_execute_result


@pytest.fixture
def mock_google_sso() -> MagicMock:
    sso = MagicMock()
    sso.__aenter__ = AsyncMock(return_value=sso)
    sso.__aexit__ = AsyncMock(return_value=None)
    sso.get_login_redirect = AsyncMock(
        return_value=RedirectResponse("https://accounts.google.com/o/oauth2/auth")
    )
    return sso


@pytest.fixture
def auth_client(mock_db: AsyncMock, mock_google_sso: MagicMock) -> Generator[TestClient, None, None]:
    async def override_get_db():
        yield mock_db

    def override_get_google_sso() -> MagicMock:
        return mock_google_sso

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_google_sso] = override_get_google_sso

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_login_redirects_to_google(auth_client: TestClient, mock_google_sso: MagicMock) -> None:
    response = auth_client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://accounts.google.com/o/oauth2/auth"
    mock_google_sso.get_login_redirect.assert_awaited_once()


def test_callback_redirects_with_token_on_success(
    auth_client: TestClient,
    mock_db: AsyncMock,
    mock_google_sso: MagicMock,
    mock_user: User,
) -> None:
    google_user = MagicMock()
    google_user.id = "google-123"
    google_user.email = "teacher@example.com"
    google_user.display_name = "Test Teacher"
    google_user.picture = "https://example.com/avatar.png"

    mock_google_sso.verify_and_process = AsyncMock(return_value=google_user)
    mock_db.execute = AsyncMock(return_value=mock_execute_result([]))

    async def assign_user_on_refresh(user: User) -> None:
        if user.id is None:
            user.id = mock_user.id

    mock_db.refresh.side_effect = assign_user_on_refresh

    response = auth_client.get("/auth/callback?code=test-code", follow_redirects=False)

    assert response.status_code == 307
    location = urlparse(response.headers["location"])
    assert location.scheme in {"http", "https"}
    assert location.netloc
    query = parse_qs(location.query)
    assert "token" in query
    assert query["token"][0]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


def test_callback_redirects_on_sso_failure(
    auth_client: TestClient,
    mock_google_sso: MagicMock,
) -> None:
    mock_google_sso.verify_and_process = AsyncMock(side_effect=Exception("invalid code"))

    response = auth_client.get("/auth/callback?code=bad-code", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == f"{settings.frontend_url}?auth_error=true"
