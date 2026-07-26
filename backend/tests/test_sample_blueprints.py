from app.schemas.generation import QuestionPaperBlueprint
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
