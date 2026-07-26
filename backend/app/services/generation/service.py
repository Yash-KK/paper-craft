from pathlib import Path

from app.schemas.generation import GenerationResult, QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.documents import DEFAULT_FORMAT_REFERENCE_URI, to_file_uri
from app.services.generation.format_reference import resolve_format_reference
from app.services.generation.graph import generation_graph


def generate_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    teacher_instructions: str | None = None,
    format_reference_uri: str | None = None,
    format_reference_upload: Path | None = None,
) -> GenerationResult:
    """Plan slots from an editable blueprint → retrieve → generate → assemble."""
    if format_reference_upload is not None:
        uri = to_file_uri(format_reference_upload)
        is_default = False
    else:
        uri = format_reference_uri or DEFAULT_FORMAT_REFERENCE_URI
        is_default = True

    # Materialize now so missing/invalid refs fail before the LLM graph runs.
    resolve_format_reference(uri)

    result = generation_graph.invoke(
        {
            "question_paper": blueprint.model_dump(mode="json"),
            "selected_chapters": [c.model_dump() for c in selected_chapters],
            "subject": subject,
            "grade": grade,
            "teacher_instructions": (teacher_instructions or "").strip() or None,
        }
    )

    return GenerationResult(
        blueprint=blueprint,
        final_paper=result["final_paper"] or {"sections": {}},
        final_answer_key=result["final_answer_key"] or {"sections": {}},
        generated_items=result.get("generated_items") or [],
        format_reference_uri=uri,
        format_reference_is_default=is_default,
    )
