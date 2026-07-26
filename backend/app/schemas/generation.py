from datetime import date, datetime
from enum import Enum
from typing import Any, Self, TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.db.models.notebook import Board, ClassGrade, Subject
from app.db.models.question_paper import QuestionPaperStatus
from app.schemas.notebook import SelectedChapter


class BlueprintKind(str, Enum):
    """High-level template family. Controls marks validation and UI framing."""

    EXAM = "EXAM"
    REVISION_SHEET = "REVISION_SHEET"
    # Future: UNIT_TEST, ASSIGNMENT, PRACTICE_SET, …


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


class BlueprintSubPart(BaseModel):
    """Template for CASE_STUDY (or similar) parts applied to every question in a section."""

    label: str = Field(description="Part label, e.g. 'i', 'ii', 'iii'.")
    marks: float | None = Field(
        default=None,
        description="Optional marks for this part; omit for non-mark blueprints.",
    )


class BlueprintSection(BaseModel):
    section_name: str = Field(
        description="Display name for the section, e.g. 'MCQ', 'VSA', 'CBQ'."
    )
    question_type: QuestionType = Field(
        description="Question type for this section (CBQ maps to CASE_STUDY)."
    )
    marks_each: float | None = Field(
        default=None,
        description="Marks per question in this section; null for non-mark blueprints.",
    )
    chapter_allocations: list[ChapterAllocation] = Field(
        default_factory=list,
        description="Per-chapter question counts within this section.",
    )
    section_instructions: str | None = Field(
        default=None,
        description="Optional notes at the section header.",
    )
    sub_parts: list[BlueprintSubPart] = Field(
        default_factory=list,
        description="Optional sub-part template (e.g. Case Study (i)/(ii)/(iii)).",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def section_total_marks(self) -> float | None:
        if self.marks_each is None and all(a.marks is None for a in self.chapter_allocations):
            return None
        total = 0.0
        for allocation in self.chapter_allocations:
            per_question = (
                allocation.marks if allocation.marks is not None else self.marks_each
            )
            if per_question is None:
                return None
            total += allocation.question_count * per_question
        return total

    @computed_field  # type: ignore[prop-decorator]
    @property
    def question_count(self) -> int:
        return sum(a.question_count for a in self.chapter_allocations)


class QuestionPaperBlueprint(BaseModel):
    kind: BlueprintKind = Field(
        default=BlueprintKind.EXAM,
        description="Template family — exam, revision sheet, etc.",
    )
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
    total_marks: int | None = Field(
        default=None,
        description="Target total marks when kind is mark-based; null otherwise.",
    )
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
    learning_outcomes: list[str] = Field(
        default_factory=list,
        description="Optional learning outcomes covered by this blueprint.",
    )
    generation_rules: list[str] = Field(
        default_factory=list,
        description=(
            "Prompt-facing generation guidance for this blueprint kind "
            "(e.g. revision vs examination tone)."
        ),
    )
    sections: list[BlueprintSection] = Field(
        description="Ordered question-type sections making up the paper.",
    )
    blooms_targets: dict[BloomsLevel, float] | None = Field(
        default=None,
        description="Optional Bloom's mark targets from the sample template.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible blueprint-specific metadata without schema changes.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allocated_marks(self) -> float | None:
        totals = [section.section_total_marks for section in self.sections]
        if any(total is None for total in totals):
            return None
        return float(sum(totals))  # type: ignore[arg-type]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_mark_based(self) -> bool:
        return self.kind == BlueprintKind.EXAM

    @model_validator(mode="after")
    def validate_marks_consistency(self) -> Self:
        if not self.is_mark_based:
            return self
        if self.total_marks is None:
            raise ValueError("EXAM blueprints require total_marks")
        for section in self.sections:
            if section.marks_each is None and any(
                a.marks is None for a in section.chapter_allocations
            ):
                raise ValueError(
                    f"EXAM section '{section.section_name}' requires marks_each "
                    "or per-allocation marks"
                )
        if self.allocated_marks is None:
            raise ValueError("EXAM blueprints must allocate marks across sections")
        if abs(self.allocated_marks - self.total_marks) > 1e-9:
            raise ValueError(
                f"section allocations total {self.allocated_marks:g} marks, "
                f"but total_marks is {self.total_marks}"
            )
        return self


class SlotSubPart(BaseModel):
    label: str
    marks: float | None = None
    has_internal_choice: bool = False


class Slot(BaseModel):
    slot_id: str
    section_name: str
    question_number: int
    question_type: QuestionType
    marks: float | None = None
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
        default_factory=list,
        description="Steps whose marks sum exactly to the required marks when mark-based.",
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
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    label: str
    kind: BlueprintKind = BlueprintKind.EXAM
    total_marks: int | None = None
    board: Board | None = None
    subject: Subject | None = None
    grade: ClassGrade | None = None
    format_reference_uri: str | None = None


class SampleBlueprintDetail(SampleBlueprintSummary):
    blueprint: QuestionPaperBlueprint


class GeneratePaperRequest(BaseModel):
    """Request body for first-time question paper generation (creates Version 1)."""

    notebook_id: UUID
    blueprint: QuestionPaperBlueprint
    selected_chapters: list[SelectedChapter]
    subject: str
    grade: int
    title: str | None = None
    teacher_instructions: str | None = None
    format_reference_uri: str | None = None


class GenerateNewVersionRequest(BaseModel):
    """Create the next version from the latest ready version + selected chat context."""

    selected_message_ids: list[UUID] = Field(default_factory=list)
    teacher_instructions: str | None = None


class SelectedChatMessageSnapshot(BaseModel):
    id: UUID
    role: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class GeneratedPaperOutput(BaseModel):
    """Sync graph output before persistence onto a version row."""

    blueprint: QuestionPaperBlueprint
    final_paper: dict
    final_answer_key: dict
    generated_items: list[dict]
    format_reference_uri: str
    format_reference_is_default: bool = True


class GenerationResult(BaseModel):
    """Accepted/queued (or completed) version response."""

    paper_id: UUID
    version_id: UUID
    notebook_id: UUID
    title: str
    version_number: int
    status: QuestionPaperStatus
    blueprint: QuestionPaperBlueprint
    final_paper: dict
    final_answer_key: dict
    generated_items: list[dict]
    format_reference_uri: str
    format_reference_is_default: bool = True
    paper_markdown: str = ""
    answer_key_markdown: str = ""
    selected_chat_messages: list[SelectedChatMessageSnapshot] = Field(
        default_factory=list
    )
    error: str | None = None


class QuestionPaperVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_number: int
    status: QuestionPaperStatus
    subject: str
    grade: int
    format_reference_uri: str
    format_reference_is_default: bool
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    base_version_id: UUID | None = None


class QuestionPaperSummary(BaseModel):
    """Parent paper with nested version summaries for sidebar grouping."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notebook_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    versions: list[QuestionPaperVersionSummary] = Field(default_factory=list)
    latest_version: QuestionPaperVersionSummary | None = None


class QuestionPaperVersionDetail(QuestionPaperVersionSummary):
    question_paper_id: UUID
    notebook_id: UUID
    title: str
    blueprint: QuestionPaperBlueprint
    final_paper: dict
    final_answer_key: dict
    generated_items: list[dict]
    selected_chapters: list[SelectedChapter] = Field(default_factory=list)
    selected_chat_messages: list[SelectedChatMessageSnapshot] = Field(
        default_factory=list
    )
    teacher_instructions: str | None = None
    generation_context: dict[str, Any] = Field(default_factory=dict)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    paper_markdown: str = ""
    answer_key_markdown: str = ""


class GenerationState(TypedDict):
    question_paper: dict
    selected_chapters: list[dict]
    subject: str
    grade: int
    teacher_instructions: str | None
    slots: list[dict]
    generated_items: list[dict]
    final_paper: dict | None
    final_answer_key: dict | None
    revision_context: dict | None
