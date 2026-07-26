from app.schemas.generation import GenerationResult, QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.generation.graph import generation_graph


def generate_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    teacher_instructions: str | None = None,
    use_sample_as_context: bool = False,
    sample_text: str | None = None,
) -> GenerationResult:
    """Plan slots from an editable blueprint → retrieve → generate → assemble."""
    instructions = (teacher_instructions or "").strip() or None
    style_text = sample_text if use_sample_as_context else None

    initial_state = {
        "question_paper": blueprint.model_dump(mode="json"),
        "selected_chapters": [c.model_dump() for c in selected_chapters],
        "subject": subject,
        "grade": grade,
        "teacher_instructions": instructions,
        "use_sample_as_context": use_sample_as_context,
        "sample_text": style_text,
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
        sample_text_used=bool(use_sample_as_context and style_text),
    )
