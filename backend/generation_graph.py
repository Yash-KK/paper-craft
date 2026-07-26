"""Thin demo for the generation service.

Prefer importing from app.services.generation directly in new code.
"""

from app.schemas.generation import QuestionPaperBlueprint
from app.schemas.notebook import SelectedChapter
from app.services.generation import generate_paper
from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT

# %%
selected_chapters = [
    SelectedChapter(
        book_code="jemh1",
        chapter_number=1,
        chapter_name="Real Numbers",
    ),
    SelectedChapter(
        book_code="jemh1",
        chapter_number=2,
        chapter_name="Polynomials",
    ),
    SelectedChapter(
        book_code="jemh1",
        chapter_number=3,
        chapter_name="Pair of Linear Equations in Two Variables",
    ),
]

# %%
if __name__ == "__main__":
    blueprint = QuestionPaperBlueprint.model_validate(FORTY_MARKS_BLUEPRINT)
    result = generate_paper(
        blueprint=blueprint,
        selected_chapters=selected_chapters,
        subject="Mathematics",
        grade=10,
        teacher_instructions="Focus more on application-based questions.",
    )
    print("format reference:", result.format_reference_uri)
    print("using default sample:", result.format_reference_is_default)
    print("blueprint title:", result.blueprint.exam_title)
    print("allocated / total:", result.blueprint.allocated_marks, "/", result.blueprint.total_marks)
    print("sections:", list((result.final_paper or {}).get("sections", {}).keys()))
    print("items:", len(result.generated_items))
