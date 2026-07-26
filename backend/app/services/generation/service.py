from pathlib import Path

from app.schemas.generation import GenerationResult, QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.generation.format_reference import resolve_format_reference
from app.services.generation.graph import generation_graph


def generate_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    teacher_instructions: str | None = None,
    format_reference_path: Path | None = None,
) -> GenerationResult:
    """Plan slots from an editable blueprint → retrieve → generate → assemble."""
    instructions = (teacher_instructions or "").strip() or None
    is_default = format_reference_path is None
    reference = resolve_format_reference(format_reference_path)

    initial_state = {
        "question_paper": blueprint.model_dump(mode="json"),
        "selected_chapters": [c.model_dump() for c in selected_chapters],
        "subject": subject,
        "grade": grade,
        "teacher_instructions": instructions,
        "format_reference_path": str(reference),
        "slots": [],
        "generated_items": [],
        "final_paper": None,
        "final_answer_key": None,
    }

    result = generation_graph.invoke(initial_state)

    return GenerationResult(
        blueprint=QuestionPaperBlueprint.model_validate(result["question_paper"]),
        final_paper=result["final_paper"] or {"sections": {}},
        final_answer_key=result["final_answer_key"] or {"sections": {}},
        generated_items=result.get("generated_items") or [],
        format_reference_path=str(reference),
        format_reference_is_default=is_default,
    )
