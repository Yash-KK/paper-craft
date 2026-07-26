"""Thin demo for the generation service.

Prefer importing from app.services.generation directly in new code.
"""

from pathlib import Path

from app.schemas.notebook import SelectedChapter
from app.services.generation import generate_paper

# %%
DOCX_PATH = Path(__file__).resolve().parent / "notebooks" / "sample.docx"
# DOCX_PATH = Path(__file__).resolve().parent / "notebooks" / "revision_sheet.docx"

selected_chapters = [
    SelectedChapter(
        book_code="jemh1",
        chapter_number=1,
        chapter_name="Real Numbers",
    ),
]

# %%
if __name__ == "__main__":
    result = generate_paper(
        docx_path=DOCX_PATH,
        selected_chapters=selected_chapters,
        subject="mathematics",
        grade=10,
        use_sample_as_context=True,
    )
    print("sample_text_used:", result.sample_text_used)
    print("blueprint title:", result.blueprint.exam_title)
    print("sections:", list((result.final_paper or {}).get("sections", {}).keys()))
    print("items:", len(result.generated_items))
