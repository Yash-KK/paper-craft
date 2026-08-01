"""Next question-paper version: one prompt, one LLM call, persist result.

Inputs are the previous version JSON, selected chat messages, and optional
teacher instructions. No LangGraph / retrieval / multi-stage orchestration.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models.question_paper import (
    QuestionPaper,
    QuestionPaperStatus,
    QuestionPaperVersion,
)
from app.db.session import get_sync_db
from app.schemas.generation import GeneratedPaperOutput, QuestionPaperBlueprint
from app.services.chat.llm import get_chat_model
from app.services.export.section_copy import resolve_final_paper
from app.services.generation.assemble import assemble_final_paper

logger = logging.getLogger(__name__)

NEXT_VERSION_SYSTEM = """You revise an existing school question paper.

You receive the previous ready version as JSON (student paper and generated
item records), plus selected teacher chat messages and optional teacher
instructions.

Rules:
- Preserve the previous structure (sections, question numbers, types, marks,
  chapter assignments, internal-choice flags) unless chat/instructions
  explicitly require a change.
- Apply only what the chat messages and teacher instructions ask for.
- Leave unchanged questions as they were.
- Keep questions academically correct, unambiguous, and fully solvable.
- Return a complete revised paper: final_paper and generated_items must stay
  aligned with each other and use the same field shapes as the previous version.
- Do not invent new top-level fields. Do not drop questions unless asked.
- Do not include answers, marking rubrics, or answer keys.
"""


class NextVersionContent(BaseModel):
    """Structured LLM output for a revised question-paper version."""

    final_paper: dict[str, Any] = Field(
        description="Revised student-facing paper; same shape as previous final_paper"
    )
    generated_items: list[dict[str, Any]] = Field(
        description="Full revised item records; same shape as previous generated_items"
    )


def _paper_title(blueprint: QuestionPaperBlueprint) -> str:
    return (blueprint.exam_title or "").strip() or "Question Paper"


def _touch_parent(paper: QuestionPaper) -> None:
    paper.updated_at = datetime.now(UTC)


def _format_chat_messages(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = (message.get("role") or "user").upper()
        content = (message.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    if not lines:
        return "(none)"
    return "\n".join(lines)


def build_next_version_messages(
    *,
    previous_final_paper: dict[str, Any],
    previous_generated_items: list[dict[str, Any]],
    selected_chat_messages: list[dict[str, Any]],
    teacher_instructions: str | None,
) -> list[tuple[str, str]]:
    """Build the single system + human prompt for next-version generation."""
    instructions = (teacher_instructions or "").strip()
    teacher_block = instructions or "(none)"

    human = f"""PREVIOUS FINAL PAPER (JSON):
{json.dumps(previous_final_paper, ensure_ascii=False, indent=2)}

PREVIOUS GENERATED ITEMS (JSON):
{json.dumps(previous_generated_items, ensure_ascii=False, indent=2)}

SELECTED CHAT MESSAGES:
{_format_chat_messages(selected_chat_messages)}

TEACHER INSTRUCTIONS:
{teacher_block}

Return the complete revised final_paper and generated_items.
"""
    return [
        ("system", NEXT_VERSION_SYSTEM),
        ("human", human),
    ]


def generate_next_version_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    previous_final_paper: dict[str, Any],
    previous_generated_items: list[dict[str, Any]],
    selected_chat_messages: list[dict[str, Any]],
    teacher_instructions: str | None,
) -> GeneratedPaperOutput:
    """Single LLM call → structured NextVersionContent → GeneratedPaperOutput."""
    messages = build_next_version_messages(
        previous_final_paper=previous_final_paper,
        previous_generated_items=previous_generated_items,
        selected_chat_messages=selected_chat_messages,
        teacher_instructions=teacher_instructions,
    )
    structured_llm = (
        get_chat_model()
        .bind(max_tokens=16000)
        .with_structured_output(NextVersionContent)
    )
    result = structured_llm.invoke(messages)
    content = (
        result
        if isinstance(result, NextVersionContent)
        else NextVersionContent.model_validate(result)
    )
    items = [item for item in (content.generated_items or []) if isinstance(item, dict)]
    # Prefer assembling the student paper from items so section values stay
    # list[dict] even when the model returns a malformed final_paper.
    if items:
        final_paper = assemble_final_paper(items)
    else:
        final_paper = resolve_final_paper(content.final_paper)
    return GeneratedPaperOutput(
        blueprint=blueprint,
        final_paper=final_paper,
        generated_items=items,
    )


def run_next_version_generation(version_id: UUID, *, db: Session | None = None) -> None:
    """Sync worker: generate the next version from its base version + chat context."""

    def _run(session: Session) -> None:
        version = session.get(QuestionPaperVersion, version_id)
        if version is None:
            logger.warning(
                "Version %s not found; skipping next-version generation", version_id
            )
            return

        paper = session.get(QuestionPaper, version.question_paper_id)
        if paper is None:
            logger.warning("Parent paper missing for version %s; skipping", version_id)
            return

        if version.status == QuestionPaperStatus.READY:
            logger.info("Version %s already ready; skipping", version_id)
            return

        if version.status == QuestionPaperStatus.FAILED:
            logger.info(
                "Version %s previously failed; skipping unless re-queued",
                version_id,
            )
            return

        if version.base_version_id is None:
            raise ValueError(
                "Next-version generation requires base_version_id "
                f"(version_id={version_id})"
            )

        started_at = datetime.now(UTC)
        version.status = QuestionPaperStatus.RUNNING
        version.error = None
        metadata = dict(version.generation_metadata or {})
        metadata.update(
            {
                "started_at": started_at.isoformat(),
                "worker": "celery",
                "task": "generate_next_question_paper_version",
            }
        )
        version.generation_metadata = metadata
        _touch_parent(paper)
        session.commit()

        try:
            context = version.generation_context or {}
            previous_items = list(
                context.get("base_generated_items") or version.generated_items or []
            )
            previous_final_paper = dict(
                context.get("base_final_paper") or version.final_paper or {}
            )
            if not previous_items and not previous_final_paper:
                raise ValueError(
                    "Previous version content is empty — cannot generate next version "
                    f"(version_id={version_id})"
                )

            blueprint = QuestionPaperBlueprint.model_validate(version.blueprint)
            result = generate_next_version_paper(
                blueprint=blueprint,
                previous_final_paper=previous_final_paper,
                previous_generated_items=previous_items,
                selected_chat_messages=list(version.selected_chat_messages or []),
                teacher_instructions=version.teacher_instructions,
            )

            finished_at = datetime.now(UTC)
            version.status = QuestionPaperStatus.READY
            version.blueprint = result.blueprint.model_dump(mode="json")
            version.final_paper = result.final_paper
            version.generated_items = result.generated_items
            version.error = None
            metadata = dict(version.generation_metadata or {})
            metadata.update(
                {
                    "finished_at": finished_at.isoformat(),
                    "duration_seconds": (finished_at - started_at).total_seconds(),
                }
            )
            version.generation_metadata = metadata
            if not paper.title.strip():
                paper.title = _paper_title(result.blueprint)
            _touch_parent(paper)
            session.commit()
            logger.info("Version %s next-version generation completed", version_id)
        except Exception as exc:
            session.rollback()
            version = session.get(QuestionPaperVersion, version_id)
            paper = (
                session.get(QuestionPaper, version.question_paper_id)
                if version is not None
                else None
            )
            if version is not None:
                version.status = QuestionPaperStatus.FAILED
                version.error = str(exc)
                metadata = dict(version.generation_metadata or {})
                metadata["failed_at"] = datetime.now(UTC).isoformat()
                version.generation_metadata = metadata
                if paper is not None:
                    _touch_parent(paper)
                session.commit()
            logger.exception("Version %s next-version generation failed", version_id)
            raise

    if db is not None:
        _run(db)
    else:
        with get_sync_db() as session:
            _run(session)
