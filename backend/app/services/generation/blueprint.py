"""Legacy DOCX → blueprint LLM extraction.

The primary generate path now uses editable Sample Blueprints / form payloads
instead of calling this. Kept for offline experiments only.
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.services.chat.llm import get_chat_model

# Minimal schema so structured output still works for notebook experiments.
# Production blueprints use app.schemas.generation.QuestionPaperBlueprint.


class _LegacyQuestionSpec(BaseModel):
    question_number: int
    question_type: str
    marks: float
    has_internal_choice: bool = False


class _LegacySection(BaseModel):
    section_name: str
    questions: list[_LegacyQuestionSpec]
    stated_total_marks: float | None = None


class _LegacyBlueprint(BaseModel):
    school_name: str | None = None
    exam_title: str | None = None
    subject: str
    grade: int
    total_marks: int
    duration_minutes: int | None = None
    general_instructions: list[str] = Field(default_factory=list)
    sections: list[_LegacySection]


BLUEPRINT_SYSTEM_MESSAGE = """
You extract a coarse question-paper structure from raw DOCX markdown.
Map questions into sections; classify types as MCQ/VSA/SA/LA/CASE_STUDY/etc.
"""


def extract_blueprint(qp_text: str) -> _LegacyBlueprint:
    structured_llm = get_chat_model().with_structured_output(_LegacyBlueprint)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BLUEPRINT_SYSTEM_MESSAGE),
            (
                "user",
                "Please extract the blueprint from the following question paper text:\n\n{text}",
            ),
        ]
    )
    chain = prompt | structured_llm
    return chain.invoke({"text": qp_text})
