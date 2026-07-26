from pathlib import Path

from app.schemas.generation import GenerationResult, QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.generation.blueprint import extract_blueprint
from app.services.generation.graph import generation_graph
from app.services.generation.parse import parse_docx, truncate_sample_text


def generate_paper(
    *,
    docx_path: Path,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    use_sample_as_context: bool = False,
) -> GenerationResult:
    """Parse DOCX → extract blueprint → plan/retrieve/generate/assemble."""
    path = Path(docx_path)
    if not path.is_file():
        raise FileNotFoundError(f"DOCX not found: {path}")

    markdown, _ = parse_docx(path)
    blueprint = extract_blueprint(markdown)

    sample_text = truncate_sample_text(markdown) if use_sample_as_context else None

    initial_state = {
        "question_paper": blueprint.model_dump(mode="json"),
        "selected_chapters": [c.model_dump() for c in selected_chapters],
        "subject": subject,
        "grade": grade,
        "use_sample_as_context": use_sample_as_context,
        "sample_text": sample_text,
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
        sample_text_used=bool(use_sample_as_context and sample_text),
    )
