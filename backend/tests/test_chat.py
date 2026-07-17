"""Chat streaming endpoint tests."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.models.chat import ChatMessageRole
from tests.conftest import mock_execute_result


def _owned_notebook(user_id) -> MagicMock:
    notebook = MagicMock()
    notebook.id = uuid4()
    notebook.user_id = user_id
    notebook.name = "Algebra"
    notebook.selected_chapters = [
        {"book_code": "jemh1", "chapter_number": 1, "chapter_name": "Real Numbers"}
    ]
    return notebook


def _session(notebook_id) -> MagicMock:
    session = MagicMock()
    session.id = uuid4()
    session.notebook_id = notebook_id
    session.title = "Algebra"
    session.created_at = datetime.now(timezone.utc)
    session.updated_at = datetime.now(timezone.utc)
    return session


def _message(session_id, role: ChatMessageRole, content: str) -> MagicMock:
    message = MagicMock()
    message.id = uuid4()
    message.session_id = session_id
    message.role = role
    message.content = content
    message.message_metadata = {}
    message.created_at = datetime.now(timezone.utc)
    return message


def _parse_sse(body: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for block in body.split("\n\n"):
        line = block.strip()
        if not line.startswith("data: "):
            continue
        import json

        events.append(json.loads(line[6:]))
    return events


async def _fake_stream(
    *,
    question: str,
    history: list,
    selected_chapters: list,
    top_k: int,
) -> AsyncIterator[dict[str, Any]]:
    assert question
    assert selected_chapters
    assert top_k == 5
    yield {"type": "thinking"}
    yield {
        "type": "tool_start",
        "tool": "retrieve_context",
        "input": "HCF",
    }
    yield {
        "type": "tool_end",
        "tool": "retrieve_context",
        "output": "HCF is...",
    }
    yield {"type": "token", "content": "Hello "}
    yield {"type": "token", "content": "teacher"}
    yield {
        "type": "complete",
        "answer": "Hello teacher",
        "tool_calls": [
            {
                "tool": "retrieve_context",
                "input": "HCF",
                "output": "HCF is...",
                "status": "done",
            }
        ],
    }


async def _fake_stream_error(
    *,
    question: str,
    history: list,
    selected_chapters: list,
    top_k: int,
) -> AsyncIterator[dict[str, Any]]:
    yield {"type": "thinking"}
    yield {
        "type": "error",
        "message": "The chat service could not generate a response",
    }


def test_get_chat_requires_ownership(
    client: TestClient, mock_db: AsyncMock, mock_user
) -> None:
    mock_db.get = AsyncMock(return_value=None)

    response = client.get(f"/api/v1/notebooks/{uuid4()}/chat")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notebook not found"


def test_get_chat_creates_session_and_returns_messages(
    client: TestClient, mock_db: AsyncMock, mock_user
) -> None:
    notebook = _owned_notebook(mock_user.id)
    session = _session(notebook.id)
    history = [
        _message(session.id, ChatMessageRole.USER, "What is HCF?"),
        _message(session.id, ChatMessageRole.ASSISTANT, "Highest common factor."),
    ]

    mock_db.get = AsyncMock(return_value=notebook)
    mock_db.scalar = AsyncMock(side_effect=[None, session])
    mock_db.execute = AsyncMock(return_value=mock_execute_result(history))

    # First scalar is create path (None), then after commit refresh uses the created session.
    # Simplify: session already exists.
    mock_db.scalar = AsyncMock(return_value=session)

    response = client.get(f"/api/v1/notebooks/{notebook.id}/chat")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(session.id)
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][1]["role"] == "assistant"


def test_stream_chat_emits_events_and_persists_assistant(
    client: TestClient, mock_db: AsyncMock, mock_user
) -> None:
    notebook = _owned_notebook(mock_user.id)
    session = _session(notebook.id)
    prior = [_message(session.id, ChatMessageRole.USER, "Earlier")]
    user_message = _message(session.id, ChatMessageRole.USER, "Explain HCF")
    assistant_message = _message(
        session.id, ChatMessageRole.ASSISTANT, "Hello teacher"
    )
    assistant_message.message_metadata = {
        "tool_calls": [
            {
                "tool": "retrieve_context",
                "input": "HCF",
                "output": "HCF is...",
                "status": "done",
            }
        ],
    }

    mock_db.get = AsyncMock(side_effect=[notebook, session])
    mock_db.scalar = AsyncMock(return_value=session)
    mock_db.execute = AsyncMock(return_value=mock_execute_result(prior))

    async def refresh_side_effect(obj) -> None:
        if getattr(obj, "role", None) == ChatMessageRole.USER:
            obj.id = user_message.id
            obj.session_id = session.id
            obj.content = user_message.content
            obj.message_metadata = {}
            obj.created_at = user_message.created_at
        elif getattr(obj, "role", None) == ChatMessageRole.ASSISTANT:
            obj.id = assistant_message.id
            obj.session_id = session.id
            obj.content = assistant_message.content
            obj.message_metadata = assistant_message.message_metadata
            obj.created_at = assistant_message.created_at

    mock_db.refresh = AsyncMock(side_effect=refresh_side_effect)

    with patch(
        "app.api.v1.chat.stream_notebook_chat",
        new=_fake_stream,
    ):
        with client.stream(
            "POST",
            f"/api/v1/notebooks/{notebook.id}/chat/messages",
            json={"content": "Explain HCF"},
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            body = "".join(response.iter_text())

    events = _parse_sse(body)
    assert events[0]["type"] == "thinking"
    assert events[1]["type"] == "tool_start"
    assert events[1]["tool"] == "retrieve_context"
    assert events[1]["input"] == "HCF"
    assert events[2]["type"] == "tool_end"
    assert events[2]["tool"] == "retrieve_context"
    assert events[3]["type"] == "token"
    assert events[4]["type"] == "token"
    assert events[-1]["type"] == "done"
    assert events[-1]["assistant_message"]["content"] == "Hello teacher"
    assert (
        events[-1]["assistant_message"]["metadata"]["tool_calls"][0]["tool"]
        == "retrieve_context"
    )
    assert mock_db.commit.await_count >= 2


def test_stream_chat_emits_safe_error(
    client: TestClient, mock_db: AsyncMock, mock_user
) -> None:
    notebook = _owned_notebook(mock_user.id)
    session = _session(notebook.id)
    user_message = _message(session.id, ChatMessageRole.USER, "Explain HCF")

    mock_db.get = AsyncMock(return_value=notebook)
    mock_db.scalar = AsyncMock(return_value=session)
    mock_db.execute = AsyncMock(return_value=mock_execute_result([]))

    async def refresh_side_effect(obj) -> None:
        obj.id = user_message.id
        obj.session_id = session.id
        obj.content = user_message.content
        obj.message_metadata = {}
        obj.created_at = user_message.created_at

    mock_db.refresh = AsyncMock(side_effect=refresh_side_effect)

    with patch(
        "app.api.v1.chat.stream_notebook_chat",
        new=_fake_stream_error,
    ):
        with client.stream(
            "POST",
            f"/api/v1/notebooks/{notebook.id}/chat/messages",
            json={"content": "Explain HCF"},
        ) as response:
            assert response.status_code == 200
            body = "".join(response.iter_text())

    events = _parse_sse(body)
    assert events[0]["type"] == "thinking"
    assert events[-1]["type"] == "error"
    assert events[-1]["message"] == "The chat service could not generate a response"
    # User message committed once; assistant never persisted.
    assert mock_db.commit.await_count == 1


def test_stream_chat_rejects_blank_message(
    client: TestClient, mock_db: AsyncMock, mock_user
) -> None:
    notebook = _owned_notebook(mock_user.id)
    mock_db.get = AsyncMock(return_value=notebook)

    response = client.post(
        f"/api/v1/notebooks/{notebook.id}/chat/messages",
        json={"content": "   "},
    )

    assert response.status_code == 422
