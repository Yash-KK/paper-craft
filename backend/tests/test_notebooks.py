from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.models.notebook import ClassGrade, Notebook, Subject
from app.db.models.user import User
from app.main import app
from tests.conftest import make_catalog_chapter, mock_execute_result


def test_create_notebook_success(
    client: TestClient,
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    chapter = make_catalog_chapter(2, "Polynomials")
    mock_db.execute = AsyncMock(return_value=mock_execute_result([chapter]))

    async def assign_id_on_refresh(notebook: Notebook) -> None:
        notebook.id = uuid4()
        notebook.created_at = datetime.now(timezone.utc)
        notebook.updated_at = datetime.now(timezone.utc)

    mock_db.refresh.side_effect = assign_id_on_refresh

    response = client.post(
        "/api/v1/notebooks",
        json={
            "name": "Mid-Term Prep",
            "class_grade": "Class 10",
            "subject": "Mathematics",
            "color_hex": "#6A0DAD",
            "selected_chapter_numbers": [2],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Mid-Term Prep"
    assert body["class_grade"] == "Class 10"
    assert body["subject"] == "Mathematics"
    assert body["selected_chapters"] == [
        {
            "book_code": "jemh1",
            "chapter_number": 2,
            "chapter_name": "Polynomials",
        }
    ]
    mock_db.add.assert_called_once()
    added_notebook = mock_db.add.call_args.args[0]
    assert added_notebook.user_id == mock_user.id
    mock_db.commit.assert_awaited_once()


def test_create_notebook_rejects_invalid_chapters(
    client: TestClient,
    mock_db: AsyncMock,
) -> None:
    mock_db.execute = AsyncMock(return_value=mock_execute_result([]))

    response = client.post(
        "/api/v1/notebooks",
        json={
            "name": "Bad Notebook",
            "class_grade": "Class 10",
            "subject": "Mathematics",
            "selected_chapter_numbers": [99],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid chapter selection"
    mock_db.add.assert_not_called()


def test_delete_notebook_success(
    client: TestClient,
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    notebook_id = uuid4()
    notebook = Notebook(
        id=notebook_id,
        user_id=mock_user.id,
        name="To Delete",
        class_grade=ClassGrade.CLASS_10,
        subject=Subject.MATHEMATICS,
        selected_chapters=[],
    )
    mock_db.get = AsyncMock(return_value=notebook)

    response = client.delete(f"/api/v1/notebooks/{notebook_id}")

    assert response.status_code == 204
    mock_db.delete.assert_awaited_once_with(notebook)
    mock_db.commit.assert_awaited_once()


def test_delete_notebook_not_found(
    client: TestClient,
    mock_db: AsyncMock,
) -> None:
    mock_db.get = AsyncMock(return_value=None)

    response = client.delete(f"/api/v1/notebooks/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notebook not found"
    mock_db.delete.assert_not_awaited()


def test_notebooks_require_auth(mock_db: AsyncMock) -> None:
    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.post(
            "/api/v1/notebooks",
            json={
                "name": "No Auth",
                "class_grade": "Class 10",
                "subject": "Mathematics",
                "selected_chapter_numbers": [1],
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 401
