from datetime import date
from enum import Enum
from typing import Self, TypedDict
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, model_validator

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


class BloomsLevel(str, Enum):
    REMEMBERING = "REMEMBERING"
    UNDERSTANDING = "UNDERSTANDING"
    APPLYING = "APPLYING"
    ANALYSING = "ANALYSING"
    EVALUATING = "EVALUATING"
    CREATING = "CREATING"


class ChapterAllocation(BaseModel):
    chapter_number: int | None = Field(
        default=None,
        description="Catalog chapter number when known; null until rematched to notebook chapters.",
    )
    chapter_name: str = Field(description="Lesson / chapter display name.")
    question_count: int = Field(ge=1, description="Number of questions for this chapter in the section.")
    blooms_level: BloomsLevel | None = Field(
        default=None,
        description="Optional Bloom's level for generation; not shown as a form section.",
    )
    has_internal_choice: bool = False
    is_assertion_reason: bool = Field(
        default=False,
        description="True for Assertion-Reason items nested under an MCQ section.",
    )
    marks: float | None = Field(
        default=None,
        description="Optional per-allocation marks override; defaults to section marks_each.",
    )


class BlueprintSection(BaseModel):
    section_name: str = Field(
        description="Display name for the section, e.g. 'MCQ', 'VSA', 'CBQ'."
    )
    question_type: QuestionType = Field(
        description="Question type for this section (CBQ maps to CASE_STUDY)."
    )
    marks_each: float = Field(description="Marks per question in this section.")
    chapter_allocations: list[ChapterAllocation] = Field(
        default_factory=list,
        description="Per-chapter question counts within this section.",
    )
    section_instructions: str | None = Field(
        default=None,
        description="Optional notes at the section header.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def section_total_marks(self) -> float:
        return sum(
            a.question_count * (a.marks if a.marks is not None else self.marks_each)
            for a in self.chapter_allocations
        )


class QuestionPaperBlueprint(BaseModel):
    school_name: str | None = Field(
        default=None,
        description="Institution name; null if absent.",
    )
    exam_title: str | None = Field(
        default=None,
        description="Exam / sheet title (e.g. 'Pre-Mid Term Examination').",
    )
    subject: str = Field(description="Subject domain, e.g. 'Mathematics'.")
    grade: int = Field(description="Class / grade level, e.g. 10.")
    total_marks: int = Field(description="Target total marks for the paper.")
    duration_minutes: int | None = Field(
        default=None,
        description="Duration in minutes (e.g. '2 Hours' -> 120); null if absent.",
    )
    exam_date: date | None = Field(
        default=None,
        description="Scheduled exam date if set.",
    )
    general_instructions: list[str] = Field(
        default_factory=list,
        description=(
            "Editable General Instructions template items included in the final paper "
            "and question-generation prompt."
        ),
    )
    sections: list[BlueprintSection] = Field(
        description="Ordered question-type sections making up the paper.",
    )
    blooms_targets: dict[BloomsLevel, float] | None = Field(
        default=None,
        description="Optional Bloom's mark targets from the sample template.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allocated_marks(self) -> float:
        return sum(section.section_total_marks for section in self.sections)

    @model_validator(mode="after")
    def validate_allocated_marks(self) -> Self:
        if abs(self.allocated_marks - self.total_marks) > 1e-9:
            raise ValueError(
                f"section allocations total {self.allocated_marks:g} marks, "
                f"but total_marks is {self.total_marks}"
            )
        return self


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
    blooms_level: BloomsLevel | None = None
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


class SampleBlueprintSummary(BaseModel):
    id: UUID
    slug: str
    label: str
    total_marks: int


class SampleBlueprintDetail(SampleBlueprintSummary):
    blueprint: QuestionPaperBlueprint


class GeneratePaperRequest(BaseModel):
    """Request body for question paper generation."""

    blueprint: QuestionPaperBlueprint
    selected_chapters: list[SelectedChapter]
    subject: str
    grade: int
    teacher_instructions: str | None = None


class GenerationResult(BaseModel):
    blueprint: QuestionPaperBlueprint
    final_paper: dict
    final_answer_key: dict
    generated_items: list[dict]
    format_reference_path: str
    format_reference_is_default: bool = True


class GenerationState(TypedDict):
    question_paper: dict
    selected_chapters: list[dict]
    subject: str
    grade: int
    teacher_instructions: str | None
    format_reference_path: str | None
    slots: list[dict]
    generated_items: list[dict]
    final_paper: dict | None
    final_answer_key: dict | None
