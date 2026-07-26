"""Tests for question paper parent/version APIs and service helpers."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.question_paper import (
    QuestionPaper,
    QuestionPaperStatus,
    QuestionPaperVersion,
)
from app.db.models.user import User
from app.schemas.generation import GenerateNewVersionRequest, GeneratePaperRequest
from app.services.generation import generate as generate_mod
from app.services.generation.papers import (
    ActiveGenerationError,
    NoReadyVersionError,
    _to_paper_summary,
    _to_version_detail,
    enqueue_new_version,
    enqueue_paper_generation,
    fail_stuck_versions,
    run_paper_generation,
)
from app.services.generation.sample_blueprints_data import REVISION_SHEET_BLUEPRINT


def _blueprint_payload() -> dict:
    return json.loads(json.dumps(REVISION_SHEET_BLUEPRINT, default=str))


def _make_version(
    *,
    paper_id=None,
    version_number: int = 1,
    status: QuestionPaperStatus = QuestionPaperStatus.READY,
    base_version_id=None,
) -> QuestionPaperVersion:
    now = datetime.now(UTC)
    return QuestionPaperVersion(
        id=uuid4(),
        question_paper_id=paper_id or uuid4(),
        version_number=version_number,
        status=status,
        subject="Mathematics",
        grade=10,
        teacher_instructions="Keep it concise",
        selected_chapters=[
            {
                "book_code": "jemh1",
                "chapter_number": 1,
                "chapter_name": "Real Numbers",
            }
        ],
        blueprint=_blueprint_payload(),
        final_paper={"sections": {"A": [{"question_number": 1, "text": "Q1"}]}},
        final_answer_key={"sections": {"A": [{"question_number": 1, "answer": "A1"}]}},
        generated_items=[
            {
                "slot_id": "s1",
                "question_number": 1,
                "question_text": "What is a real number?",
                "question_type": "VSA",
                "marks": 1,
            }
        ],
        selected_chat_messages=[],
        generation_context={},
        generation_metadata={},
        format_reference_uri="file:///tmp/default.docx",
        format_reference_is_default=True,
        base_version_id=base_version_id,
        error=None,
        created_at=now,
        updated_at=now,
    )


def _make_paper(*, versions: list[QuestionPaperVersion] | None = None) -> QuestionPaper:
    now = datetime.now(UTC)
    paper = QuestionPaper(
        id=uuid4(),
        notebook_id=uuid4(),
        title="Revision Sheet",
        created_at=now,
        updated_at=now,
    )
    paper.versions = versions or []
    for version in paper.versions:
        version.question_paper_id = paper.id
    return paper


def test_enqueue_creates_parent_and_version_one(
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    notebook_id = uuid4()
    notebook = SimpleNamespace(id=notebook_id, user_id=mock_user.id)
    mock_db.get = AsyncMock(return_value=notebook)

    async def flush_side_effect() -> None:
        for call in mock_db.add.call_args_list:
            obj = call.args[0]
            if isinstance(obj, QuestionPaper) and getattr(obj, "id", None) is None:
                obj.id = uuid4()

    async def refresh_side_effect(obj) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = datetime.now(UTC)

    mock_db.flush = AsyncMock(side_effect=flush_side_effect)
    mock_db.refresh = AsyncMock(side_effect=refresh_side_effect)

    body = GeneratePaperRequest.model_validate(
        {
            "notebook_id": str(notebook_id),
            "blueprint": _blueprint_payload(),
            "selected_chapters": [
                {
                    "book_code": "jemh1",
                    "chapter_number": 1,
                    "chapter_name": "Real Numbers",
                }
            ],
            "subject": "Mathematics",
            "grade": 10,
            "title": "My Paper",
        }
    )

    with patch(
        "app.tasks.generation.generate_question_paper_task.delay"
    ) as delay:
        result = asyncio.run(
            enqueue_paper_generation(mock_db, user=mock_user, body=body)
        )

    added = [call.args[0] for call in mock_db.add.call_args_list]
    assert any(isinstance(obj, QuestionPaper) for obj in added)
    version = next(obj for obj in added if isinstance(obj, QuestionPaperVersion))
    assert version.version_number == 1
    assert version.status == QuestionPaperStatus.PENDING
    assert version.selected_chat_messages == []
    assert result.version_number == 1
    assert result.status == QuestionPaperStatus.PENDING
    assert result.title == "My Paper"
    delay.assert_called_once_with(str(version.id))


def test_grouped_paper_summary_includes_versions() -> None:
    v1 = _make_version(version_number=1)
    v2 = _make_version(version_number=2, status=QuestionPaperStatus.PENDING)
    paper = _make_paper(versions=[v1, v2])
    summary = _to_paper_summary(paper)
    assert len(summary.versions) == 2
    assert summary.latest_version is not None
    assert summary.latest_version.version_number == 2
    assert summary.latest_version.status == QuestionPaperStatus.PENDING


def test_enqueue_new_version_inherits_latest_ready_and_snapshots(
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    ready = _make_version(version_number=1, status=QuestionPaperStatus.READY)
    paper = _make_paper(versions=[ready])
    notebook = SimpleNamespace(id=paper.notebook_id, user_id=mock_user.id)
    message_id = uuid4()
    message = SimpleNamespace(
        id=message_id,
        role=SimpleNamespace(value="user"),
        content="Make Q1 harder",
        message_metadata={"source": "chat"},
        created_at=datetime.now(UTC),
    )

    paper_result = MagicMock()
    paper_result.scalar_one_or_none.return_value = paper
    messages_result = MagicMock()
    messages_result.scalars.return_value.all.return_value = [message]

    mock_db.execute = AsyncMock(side_effect=[paper_result, messages_result])
    mock_db.get = AsyncMock(return_value=notebook)

    async def refresh_side_effect(obj) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = datetime.now(UTC)

    mock_db.refresh = AsyncMock(side_effect=refresh_side_effect)

    body = GenerateNewVersionRequest(selected_message_ids=[message_id])
    with patch(
        "app.tasks.generation.generate_question_paper_task.delay"
    ) as delay:
        result = asyncio.run(
            enqueue_new_version(
                mock_db,
                user=mock_user,
                paper_id=paper.id,
                body=body,
            )
        )

    version = next(
        call.args[0]
        for call in mock_db.add.call_args_list
        if isinstance(call.args[0], QuestionPaperVersion)
    )
    assert version.version_number == 2
    assert version.base_version_id == ready.id
    assert version.blueprint == ready.blueprint
    assert version.subject == ready.subject
    assert version.selected_chat_messages[0]["content"] == "Make Q1 harder"
    assert version.selected_chat_messages[0]["id"] == str(message_id)
    assert version.generation_context["base_version_id"] == str(ready.id)
    assert result.version_number == 2
    delay.assert_called_once_with(str(version.id))


def test_enqueue_new_version_rejects_foreign_messages(
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    ready = _make_version(version_number=1)
    paper = _make_paper(versions=[ready])
    notebook = SimpleNamespace(id=paper.notebook_id, user_id=mock_user.id)

    paper_result = MagicMock()
    paper_result.scalar_one_or_none.return_value = paper
    empty_messages = MagicMock()
    empty_messages.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(side_effect=[paper_result, empty_messages])
    mock_db.get = AsyncMock(return_value=notebook)

    with pytest.raises(LookupError):
        asyncio.run(
            enqueue_new_version(
                mock_db,
                user=mock_user,
                paper_id=paper.id,
                body=GenerateNewVersionRequest(selected_message_ids=[uuid4()]),
            )
        )


def test_enqueue_new_version_rejects_active_generation(
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    ready = _make_version(version_number=1)
    pending = _make_version(version_number=2, status=QuestionPaperStatus.PENDING)
    paper = _make_paper(versions=[ready, pending])
    notebook = SimpleNamespace(id=paper.notebook_id, user_id=mock_user.id)
    paper_result = MagicMock()
    paper_result.scalar_one_or_none.return_value = paper
    mock_db.execute = AsyncMock(return_value=paper_result)
    mock_db.get = AsyncMock(return_value=notebook)

    with pytest.raises(ActiveGenerationError):
        asyncio.run(
            enqueue_new_version(
                mock_db,
                user=mock_user,
                paper_id=paper.id,
                body=GenerateNewVersionRequest(selected_message_ids=[]),
            )
        )


def test_enqueue_new_version_requires_ready_base(
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    failed = _make_version(version_number=1, status=QuestionPaperStatus.FAILED)
    paper = _make_paper(versions=[failed])
    notebook = SimpleNamespace(id=paper.notebook_id, user_id=mock_user.id)
    paper_result = MagicMock()
    paper_result.scalar_one_or_none.return_value = paper
    mock_db.execute = AsyncMock(return_value=paper_result)
    mock_db.get = AsyncMock(return_value=notebook)

    with pytest.raises(NoReadyVersionError):
        asyncio.run(
            enqueue_new_version(
                mock_db,
                user=mock_user,
                paper_id=paper.id,
                body=GenerateNewVersionRequest(),
            )
        )


def test_run_paper_generation_success_and_failure() -> None:
    version = _make_version(status=QuestionPaperStatus.PENDING)
    paper = _make_paper(versions=[version])
    version.question_paper_id = paper.id

    session = MagicMock(spec=Session)
    session.get.side_effect = lambda model, obj_id: (
        version
        if model is QuestionPaperVersion
        else paper
        if model is QuestionPaper
        else None
    )

    fake_output = SimpleNamespace(
        blueprint=SimpleNamespace(
            model_dump=lambda mode="json": version.blueprint,
            exam_title="Revision Sheet",
        ),
        final_paper={"sections": {"A": []}},
        final_answer_key={"sections": {"A": []}},
        generated_items=[{"slot_id": "s1"}],
        format_reference_uri=version.format_reference_uri,
        format_reference_is_default=True,
    )

    with patch(
        "app.services.generation.papers.generate_paper",
        return_value=fake_output,
    ):
        run_paper_generation(version.id, db=session)

    assert version.status == QuestionPaperStatus.READY
    assert version.generated_items == [{"slot_id": "s1"}]
    assert session.commit.call_count >= 2

    version.status = QuestionPaperStatus.PENDING
    version.error = None
    with patch(
        "app.services.generation.papers.generate_paper",
        side_effect=RuntimeError("boom"),
    ), pytest.raises(RuntimeError):
        run_paper_generation(version.id, db=session)
    assert version.status == QuestionPaperStatus.FAILED
    assert version.error == "boom"


def test_fail_stuck_versions_marks_running_rows() -> None:
    stuck = _make_version(status=QuestionPaperStatus.RUNNING)
    stuck.updated_at = datetime.now(UTC) - timedelta(minutes=60)
    paper = _make_paper(versions=[stuck])
    stuck.question_paper = paper

    session = MagicMock(spec=Session)
    result = MagicMock()
    result.scalars.return_value.all.return_value = [stuck]
    session.execute.return_value = result

    count = fail_stuck_versions(timeout_minutes=30, db=session)
    assert count == 1
    assert stuck.status == QuestionPaperStatus.FAILED
    assert "timed out" in (stuck.error or "")
    session.commit.assert_called_once()


def test_revision_prompt_includes_prior_question_and_chat() -> None:
    slot = {
        "slot_id": "s1",
        "section_name": "A",
        "question_number": 1,
        "question_type": "VSA",
        "marks": 1,
        "chapter_number": 1,
        "chapter_name": "Real Numbers",
        "has_internal_choice": False,
        "sub_parts": [],
        "context_chunks": [],
    }
    revision_context = {
        "base_generated_items": [
            {
                "question_number": 1,
                "question_text": "Old question text",
                "answer": "Old answer",
            }
        ],
        "selected_chat_messages": [
            {"role": "user", "content": "Make question 1 application-based"}
        ],
    }
    messages = generate_mod._build_batch_messages(
        [slot],
        revision_context=revision_context,
        prior_by_question_number=generate_mod._prior_items_by_question_number(
            revision_context
        ),
    )
    system_text = messages[0][1]
    human_text = messages[1][1]
    assert "REVISION MODE" in system_text
    assert "Old question text" in human_text
    assert "Make question 1 application-based" in human_text


def test_list_and_version_detail_routes(
    client: TestClient,
) -> None:
    v1 = _make_version(version_number=1)
    paper = _make_paper(versions=[v1])
    notebook = SimpleNamespace(id=paper.notebook_id, user_id=uuid4())
    summary = _to_paper_summary(paper)
    detail = _to_version_detail(paper, v1)

    with patch(
        "app.api.v1.sample_blueprints.get_owned_notebook",
        new=AsyncMock(return_value=notebook),
    ), patch(
        "app.api.v1.sample_blueprints.list_paper_summaries",
        new=AsyncMock(return_value=[summary]),
    ), patch(
        "app.api.v1.sample_blueprints.get_version_detail",
        new=AsyncMock(return_value=detail),
    ):
        listed = client.get(
            f"/api/v1/generation/notebooks/{paper.notebook_id}/papers"
        )
        assert listed.status_code == 200
        body = listed.json()
        assert body[0]["id"] == str(paper.id)
        assert body[0]["versions"][0]["version_number"] == 1

        version_resp = client.get(
            f"/api/v1/generation/papers/{paper.id}/versions/1"
        )
        assert version_resp.status_code == 200
        assert version_resp.json()["version_number"] == 1
        assert version_resp.json()["status"] == "ready"


def test_version_export_requires_ready(client: TestClient) -> None:
    pending = _make_version(status=QuestionPaperStatus.PENDING)
    paper = _make_paper(versions=[pending])

    with patch(
        "app.api.v1.sample_blueprints.get_owned_version",
        new=AsyncMock(return_value=(paper, pending)),
    ):
        response = client.get(
            f"/api/v1/generation/papers/{paper.id}/versions/1/export"
        )
    assert response.status_code == 409
    assert "not ready" in response.json()["detail"]
