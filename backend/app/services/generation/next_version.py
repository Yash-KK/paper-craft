"""Dedicated pipeline for generating the next question-paper version.

Context is the previous ready version + selected chat messages + optional
teacher instructions. Blueprint structure is reused for slot layout only;
source-document retrieval is intentionally skipped.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.db.models.question_paper import (
    QuestionPaper,
    QuestionPaperStatus,
    QuestionPaperVersion,
)
from app.db.session import get_sync_db
from app.schemas.generation import (
    GeneratedPaperOutput,
    GenerationState,
    QuestionPaperBlueprint,
)
from app.schemas.notebook import SelectedChapter
from app.services.generation.assemble import assemble_node
from app.services.generation.generate import generate_paper_node
from app.services.generation.plan import plan_slots_node

logger = logging.getLogger(__name__)


def _paper_title(blueprint: QuestionPaperBlueprint) -> str:
    return (blueprint.exam_title or "").strip() or "Question Paper"


def _touch_parent(paper: QuestionPaper) -> None:
    paper.updated_at = datetime.now(UTC)


def _seed_empty_context(state: dict) -> dict:
    """Skip textbook retrieval; revision grounding comes from the prior version."""
    slots = list(state.get("slots") or [])
    for slot in slots:
        slot["context_chunks"] = []
    return {"slots": slots}


def build_next_version_graph():
    builder = StateGraph(GenerationState)
    builder.add_node("plan_slots", plan_slots_node)
    builder.add_node("skip_retrieve", _seed_empty_context)
    builder.add_node("revise_paper", generate_paper_node)
    builder.add_node("assemble", assemble_node)

    builder.add_edge(START, "plan_slots")
    builder.add_edge("plan_slots", "skip_retrieve")
    builder.add_edge("skip_retrieve", "revise_paper")
    builder.add_edge("revise_paper", "assemble")
    builder.add_edge("assemble", END)
    return builder.compile()


next_version_graph = build_next_version_graph()


def generate_next_version_paper(
    *,
    blueprint: QuestionPaperBlueprint,
    selected_chapters: list[SelectedChapter],
    subject: str,
    grade: int,
    teacher_instructions: str | None,
    base_generated_items: list[dict[str, Any]],
    selected_chat_messages: list[dict[str, Any]],
    base_version_id: str | None = None,
    base_version_number: int | None = None,
    base_final_paper: dict[str, Any] | None = None,
) -> GeneratedPaperOutput:
    """Revise a prior version using chat guidance — independent of V1 generation."""
    revision_context = {
        "base_version_id": base_version_id,
        "base_version_number": base_version_number,
        "base_final_paper": base_final_paper or {},
        "base_generated_items": base_generated_items,
        "selected_chat_messages": selected_chat_messages,
    }
    result = next_version_graph.invoke(
        {
            "question_paper": blueprint.model_dump(mode="json"),
            "selected_chapters": [c.model_dump() for c in selected_chapters],
            "subject": subject,
            "grade": grade,
            "teacher_instructions": (teacher_instructions or "").strip() or None,
            "revision_context": revision_context,
        }
    )
    return GeneratedPaperOutput(
        blueprint=blueprint,
        final_paper=result["final_paper"] or {"sections": {}},
        final_answer_key=result["final_answer_key"] or {"sections": {}},
        generated_items=result.get("generated_items") or [],
    )


def run_next_version_generation(
    version_id: UUID, *, db: Session | None = None
) -> None:
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
            logger.warning(
                "Parent paper missing for version %s; skipping", version_id
            )
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
            base_items = (
                context.get("base_generated_items")
                or version.generated_items
                or []
            )
            if not base_items:
                raise ValueError(
                    "base_generated_items is empty — cannot revise without a "
                    "previous version"
                )

            blueprint = QuestionPaperBlueprint.model_validate(version.blueprint)
            selected_chapters = [
                SelectedChapter.model_validate(chapter)
                for chapter in (version.selected_chapters or [])
            ]

            result = generate_next_version_paper(
                blueprint=blueprint,
                selected_chapters=selected_chapters,
                subject=version.subject,
                grade=version.grade,
                teacher_instructions=version.teacher_instructions,
                base_generated_items=list(base_items),
                selected_chat_messages=list(version.selected_chat_messages or []),
                base_version_id=context.get("base_version_id")
                or str(version.base_version_id),
                base_version_number=context.get("base_version_number"),
                base_final_paper=context.get("base_final_paper")
                or version.final_paper
                or {},
            )

            finished_at = datetime.now(UTC)
            version.status = QuestionPaperStatus.READY
            version.blueprint = result.blueprint.model_dump(mode="json")
            version.final_paper = result.final_paper
            version.final_answer_key = result.final_answer_key
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
            logger.exception(
                "Version %s next-version generation failed", version_id
            )
            raise

    if db is not None:
        _run(db)
    else:
        with get_sync_db() as session:
            _run(session)
