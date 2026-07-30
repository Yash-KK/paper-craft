from app.schemas.generation import GeneratedPaperOutput, QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.generation.graph import generation_graph


def generate_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    teacher_instructions: str | None = None,
) -> GeneratedPaperOutput:
    """Plan slots from an editable blueprint → retrieve → generate → assemble."""
    result = generation_graph.invoke(
        {
            "question_paper": blueprint.model_dump(mode="json"),
            "selected_chapters": [c.model_dump() for c in selected_chapters],
            "subject": subject,
            "grade": grade,
            "teacher_instructions": (teacher_instructions or "").strip() or None,
            "revision_context": None,
        }
    )

    return GeneratedPaperOutput(
        blueprint=blueprint,
        final_paper=result["final_paper"] or {"sections": {}},
        final_answer_key=result["final_answer_key"] or {"sections": {}},
        generated_items=result.get("generated_items") or [],
    )
