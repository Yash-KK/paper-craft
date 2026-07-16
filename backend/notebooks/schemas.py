from enum import Enum
import operator
from typing import Annotated, TypedDict
from pydantic import BaseModel, Field


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
        description="True ONLY if this specific subpart item offers an alternative choice branch (e.g., '(i) Define photosynthesis OR (i) Define respiration')."
    )


class QuestionSpec(BaseModel):
    question_number: int = Field(
        description="The clean integer representing the sequential top-level question item number (e.g., 1, 2, 3)."
    )
    question_type: QuestionType = Field(
        description="The strict classification enum matching how the paper tags this question structure (e.g. MCQ, SA, LA)."
    )
    marks: float = Field(
        description="The full total points allocated to this entire question branch. If sub_parts exist, this MUST be the mathematical sum total of those sub_parts."
    )
    has_internal_choice: bool = Field(
        default=False,
        description="True if an alternative 'OR' pathway is offered for the entire question unit as a whole, or if a global choice applies to this block item."
    )
    sub_parts: list[SubPart] = Field(
        default_factory=list,
        description="An array of child sub-questions. Populate only for genuinely multi-tier or multi-part questions (like Case Study / CBQ items containing structured bits)."
    )

class Section(BaseModel):
    section_name: str = Field(
        description="The formal nomenclature of the section partition. Examples: 'SECTION A', 'PART I'. If the paper has no section breaks, default to 'Section 1'."
    )
    section_instructions: str | None = Field(
        default=None,
        description="Any operational notes, choice allowances, or constraints written explicitly at the header boundary of this specific section."
    )
    questions: list[QuestionSpec] = Field(
        description="A list containing every single top-level question spec block residing structurally inside this section container."
    )
    stated_total_marks: float | None = Field(
        default=None,
        description="The cumulative section score threshold explicitly written in the header text of this section (e.g., 'Section B (20 Marks)'). Leave null if not printed."
    )


class QuestionPaperBlueprint(BaseModel):
    school_name: str | None = Field(
        default=None,
        description="The full official name of the educational institution printed at the top header of the page. Leave null if absent."
    )
    exam_title: str | None = Field(
        default=None,
        description="The descriptive name of the test administration block. Examples: 'Pre-Board Examination', 'Term-End Exam 2025-26', 'Periodic Test 1'."
    )
    subject: str = Field(
        description="The academic course field domain being tested. Examples: 'Mathematics', 'Physics', 'Social Science'."
    )
    grade: int = Field(
        description="The numeric target class level or standard of the student cohort taking the paper (e.g., 10 for Class X, 12 for Class XII)."
    )
    total_marks: int = Field(
        description="The printed gross aggregate score maximum allowed for the entire complete examination paper (e.g., 20, 40)."
    )
    duration_minutes: int | None = Field(
        default=None,
        description="The total length of time allowed for the test session cleanly computed and normalized into flat integer minutes (e.g., '3 Hours' -> 180)."
    )
    general_instructions: list[str] = Field(
        default_factory=list,
        description="A list containing each independent, clean rule item extracted out of the 'General Instructions' preamble block at the beginning of the test paper."
    )
    sections: list[Section] = Field(
        description="The list of all ordered section arrays making up the complete operational structure of the entire question paper document."
    )



class SelectedChapter(BaseModel):
    book_code: str
    chapter_number: int
    chapter_name: str


class GenerationState(TypedDict):
    question_paper: dict
    selected_chapters: list[SelectedChapter]
    chapter_weights: dict[int, float] | None
    chapter_names: dict[int, str] | None
    subject: str
    grade: int
    paper_id: str
    slots: list[dict]
    generated_items: Annotated[list[dict], operator.add]
    final_paper: dict | None
    final_answer_key: dict | None
    review_decision: dict | None



class BloomsLevel(str, Enum):
    REMEMBERING = "REMEMBERING"
    UNDERSTANDING = "UNDERSTANDING"
    APPLYING = "APPLYING"
    ANALYSING = "ANALYSING"
    EVALUATING = "EVALUATING"
    CREATING = "CREATING"
    NOT_SPECIFIED = "NOT_SPECIFIED"
 
 
class GenerationMode(str, Enum):
    REUSE = "REUSE"      # pull a real exercise question near-verbatim (add MCQ options if needed)
    VARIANT = "VARIANT"  # adapt a worked example (same method, new numbers)
    NOVEL = "NOVEL"      # fresh question grounded in theory + examples


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
    blooms_level: BloomsLevel
    chapter_number: int
    chapter_name: str
    generation_mode: GenerationMode
    has_internal_choice: bool = False
    sub_parts: list[SlotSubPart] = Field(default_factory=list)