from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.db.models.user import User
from app.services.documents import (
    DEFAULT_FORMAT_REFERENCE_URI,
    resolve_document,
    to_local_uri,
)
from app.schemas.generation import QuestionPaperBlueprint
from app.services.generation.format_reference import (
    DEFAULT_FORMAT_REFERENCE,
    resolve_format_reference,
)
from app.services.generation.generate import _build_batch_messages
from app.services.generation.plan import build_slots
from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT
from tests.conftest import mock_execute_result


@pytest.mark.parametrize("grade", ["Class 8", "Class 9", "Class 10", "Class 11", "Class 12"])
def test_sample_blueprint_filter_ignores_grade(
    grade: str,
    client: TestClient,
    mock_db: AsyncMock,
    mock_user: User,
) -> None:
    del mock_user
    mock_db.execute = AsyncMock(return_value=mock_execute_result([]))

    response = client.get(
        "/api/v1/sample-blueprints",
        params={"board": "CBSE", "subject": "Mathematics", "grade": grade},
    )

    assert response.status_code == 200
    query = mock_db.execute.await_args.args[0]
    assert "grade" not in str(query.whereclause).lower()


def test_forty_marks_blueprint_expands_to_forty_marks():
    blueprint = QuestionPaperBlueprint.model_validate(FORTY_MARKS_BLUEPRINT)
    assert blueprint.allocated_marks == 40
    assert blueprint.total_marks == 40
    assert len(blueprint.general_instructions) == 10
    assert blueprint.general_instructions[-1] == "Use of a calculator is not allowed."

    chapters = [
        {
            "book_code": "jemh1",
            "chapter_number": 1,
            "chapter_name": "Real Numbers",
        },
        {
            "book_code": "jemh1",
            "chapter_number": 2,
            "chapter_name": "Polynomials",
        },
        {
            "book_code": "jemh1",
            "chapter_number": 3,
            "chapter_name": "Pair of Linear Equations in Two Variables",
        },
    ]
    slots = build_slots(blueprint, chapters)
    assert len(slots) == 19
    assert sum(s.marks for s in slots) == 40
    assert {s.section_name for s in slots} == {"MCQ", "VSA", "SA", "LA", "CBQ"}
    assert [s.question_number for s in slots if s.question_type.value == "ASSERTION_REASON"] == [
        9,
        10,
    ]
    assert [(s.question_number, s.marks) for s in slots[-2:]] == [(18, 4), (19, 3)]
    assert sum(1 for s in slots[-2:] if s.has_internal_choice) == 1


def test_blueprint_rejects_total_that_differs_from_sections():
    mismatched = {**FORTY_MARKS_BLUEPRINT, "total_marks": 41}

    with pytest.raises(ValidationError, match="section allocations total 40 marks"):
        QuestionPaperBlueprint.model_validate(mismatched)


def test_teacher_instructions_are_prompt_context_only():
    messages = _build_batch_messages(
        [
            {
                "slot_id": "Q1",
                "section_name": "MCQ",
                "question_type": "MCQ",
                "marks": 1,
                "chapter_number": 1,
                "chapter_name": "Real Numbers",
                "has_internal_choice": False,
                "sub_parts": [],
                "context_chunks": [],
            }
        ],
        general_instructions=[
            "All questions are compulsory.",
            "Use of a calculator is not allowed.",
        ],
        teacher_instructions="Avoid direct textbook questions.",
    )

    assert "GENERAL INSTRUCTIONS FOR THE FINAL PAPER" in messages[1][1]
    assert "1. All questions are compulsory." in messages[1][1]
    assert "2. Use of a calculator is not allowed." in messages[1][1]
    assert "TEACHER INSTRUCTIONS" in messages[1][1]
    assert "Avoid direct textbook questions." in messages[1][1]


def test_default_format_reference_resolves():
    path = resolve_format_reference()
    assert path == DEFAULT_FORMAT_REFERENCE.resolve()
    assert path.is_file()
    assert path.suffix.lower() == ".docx"


def test_document_store_resolves_local_uri():
    path = resolve_document(DEFAULT_FORMAT_REFERENCE_URI)
    assert path == resolve_document(to_local_uri("samples/40_marks_sample.docx"))
    assert path.is_file()


def test_document_store_rejects_unimplemented_s3():
    with pytest.raises(NotImplementedError, match="S3"):
        resolve_document("s3://bucket/samples/40_marks_sample.docx")
