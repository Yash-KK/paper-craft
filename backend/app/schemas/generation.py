from enum import Enum
from pathlib import Path
from typing import TypedDict

from pydantic import BaseModel, Field

from app.schemas.notebook import SelectedChapter


class QuestionType(str, Enum):
    MCQ = "MCQ"
    ASSERTION_REASON = "ASSERTION_REASON"
    VSA = "VSA"
    SA = "SA"
    LA = "LA"
    CASE_STUDY = "CASE_STUDY"
    FILL_IN_THE_BLANK = "FILL_IN_THE_BLANK"
    TRUE_FALSE = "TRUE_FALSE"
    OTHER = "OTHER"


class SubPart(BaseModel):
    label: str = Field(
        description="The index tag for the individual nested child sub-question. Examples: 'i', 'ii', 'iii', 'a', 'b', 'c'."
    )
    marks: float = Field(
        description="The specific point or mark allocation assigned strictly to this sub-question sub-item."
    )
    has_internal_choice: bool = Field(
        default=False,
        description="True ONLY if this specific subpart item offers an alternative choice branch.",
    )


class QuestionSpec(BaseModel):
    question_number: int = Field(
        description="The clean integer representing the sequential top-level question item number (e.g., 1, 2, 3)."
    )
    question_type: QuestionType = Field(
        description="The strict classification enum matching how the paper tags this question structure."
    )
    marks: float = Field(
        description="The full total points allocated to this entire question branch."
    )
    has_internal_choice: bool = Field(
        default=False,
        description="True if an alternative 'OR' pathway is offered for the entire question unit.",
    )
    sub_parts: list[SubPart] = Field(
        default_factory=list,
        description="Child sub-questions for multi-part items (e.g. Case Study).",
    )


class Section(BaseModel):
    section_name: str = Field(
        description="Section title. Examples: 'SECTION A', 'PART I'. Default to 'Section 1' if none."
    )
    section_instructions: str | None = Field(
        default=None,
        description="Notes or constraints at the section header.",
    )
    questions: list[QuestionSpec] = Field(
        description="Top-level question specs inside this section.",
    )
    stated_total_marks: float | None = Field(
        default=None,
        description="Section total if printed in the header; null otherwise.",
    )


class QuestionPaperBlueprint(BaseModel):
    school_name: str | None = Field(
        default=None,
        description="Institution name from the header; null if absent.",
    )
    exam_title: str | None = Field(
        default=None,
        description="Exam / sheet title (e.g. 'Pre-Board Examination', 'Revision Sheet').",
    )
    subject: str = Field(description="Subject domain, e.g. 'Mathematics'.")
    grade: int = Field(description="Class / grade level, e.g. 10.")
    total_marks: int = Field(description="Printed total marks for the paper.")
    duration_minutes: int | None = Field(
        default=None,
        description="Duration in minutes (e.g. '2 Hours' -> 120); null if absent.",
    )
    general_instructions: list[str] = Field(
        default_factory=list,
        description="Items from the General Instructions block.",
    )
    sections: list[Section] = Field(
        description="Ordered sections making up the paper.",
    )


class SlotSubPart(BaseModel):
    label: str
    marks: float
    has_internal_choice: bool = False


class Slot(BaseModel):
    slot_id: str
    section_name: str
    question_number: int
    question_type: QuestionType
    marks: float
    chapter_number: int
    chapter_name: str
    book_code: str | None = None
    content_types: list[str] = Field(default_factory=list)
    has_internal_choice: bool = False
    sub_parts: list[SlotSubPart] = Field(default_factory=list)


class RubricStep(BaseModel):
    description: str
    marks: float


class GeneratedQuestion(BaseModel):
    slot_id: str = Field(description="Must exactly match the slot_id given in the question spec.")
    question_text: str = Field(
        description="For ASSERTION_REASON: only Assertion (A) and Reason (R) — options are appended later."
    )
    options: list[str] | None = Field(
        default=None,
        description="Exactly 4 options if question_type is MCQ, else null",
    )
    correct_option: str | None = Field(
        default=None,
        description="'a'/'b'/'c'/'d' if MCQ or ASSERTION_REASON, else null",
    )
    answer: str
    marking_rubric: list[RubricStep] = Field(
        description="Steps whose marks sum exactly to the required marks"
    )
    alternate_question_text: str | None = Field(
        default=None,
        description="Only if has_internal_choice is true.",
    )
    alternate_answer: str | None = None
    source_chunk_ids: list[str] = Field(default_factory=list)


class GeneratedPaperResponse(BaseModel):
    items: list[GeneratedQuestion]


class GeneratePaperRequest(BaseModel):
    """API-ready request body for future routes."""

    docx_path: Path
    selected_chapters: list[SelectedChapter]
    subject: str
    grade: int
    use_sample_as_context: bool = False


class GenerationResult(BaseModel):
    blueprint: QuestionPaperBlueprint
    final_paper: dict
    final_answer_key: dict
    generated_items: list[dict]
    sample_text_used: bool = False


class GenerationState(TypedDict):
    question_paper: dict
    selected_chapters: list[dict]
    subject: str
    grade: int
    use_sample_as_context: bool
    sample_text: str | None
    slots: list[dict]
    generated_items: list[dict]
    final_paper: dict | None
    final_answer_key: dict | None
