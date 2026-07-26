import pytest
from pydantic import ValidationError

from app.schemas.generation import QuestionPaperBlueprint
from app.services.generation.format_reference import (
    DEFAULT_FORMAT_REFERENCE,
    resolve_format_reference,
)
from app.services.generation.generate import _build_batch_messages
from app.services.generation.plan import build_slots
from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT


def test_forty_marks_blueprint_expands_to_forty_marks():
    blueprint = QuestionPaperBlueprint.model_validate(FORTY_MARKS_BLUEPRINT)
    assert blueprint.allocated_marks == 40
    assert blueprint.total_marks == 40

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
    assert sum(1 for s in slots if s.question_type.value == "ASSERTION_REASON") == 2


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
        teacher_instructions="Avoid direct textbook questions.",
    )

    assert "TEACHER INSTRUCTIONS" in messages[1][1]
    assert "Avoid direct textbook questions." in messages[1][1]


def test_default_format_reference_resolves():
    path = resolve_format_reference()
    assert path == DEFAULT_FORMAT_REFERENCE.resolve()
    assert path.is_file()
    assert path.suffix.lower() == ".docx"
