"""Persist and load generated question papers and their versions."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db.models.chat import ChatMessage, ChatSession
from app.db.models.notebook import Notebook
from app.db.models.question_paper import (
    QuestionPaper,
    QuestionPaperStatus,
    QuestionPaperVersion,
)
from app.db.models.user import User
from app.db.session import get_sync_db
from app.schemas.generation import (
    GenerateNewVersionRequest,
    GeneratePaperRequest,
    GenerationResult,
    QuestionPaperBlueprint,
    QuestionPaperSummary,
    QuestionPaperVersionDetail,
    QuestionPaperVersionSummary,
    SelectedChatMessageSnapshot,
)
from app.schemas.notebook import SelectedChapter
from app.services.export import render_paper_markdown
from app.services.export.section_copy import resolve_final_paper
from app.services.generation.service import generate_paper

logger = logging.getLogger(__name__)

ACTIVE_STATUSES = (QuestionPaperStatus.PENDING, QuestionPaperStatus.RUNNING)


class ActiveGenerationError(RuntimeError):
    """Raised when a paper already has a pending/running version."""


class NoReadyVersionError(RuntimeError):
    """Raised when creating a new version without a ready base."""


def _paper_title(
    blueprint: QuestionPaperBlueprint,
    *,
    explicit: str | None = None,
) -> str:
    if explicit is not None and explicit.strip():
        return explicit.strip()
    return (blueprint.exam_title or "").strip() or "Question Paper"


def _touch_parent(paper: QuestionPaper) -> None:
    paper.updated_at = datetime.now(UTC)


def _snapshot_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(message.id),
            "role": message.role.value,
            "content": message.content,
            "metadata": message.message_metadata or {},
            "created_at": (
                message.created_at.isoformat() if message.created_at else None
            ),
        }
        for message in messages
    ]


def _parse_snapshots(
    raw: list[dict[str, Any]] | None,
) -> list[SelectedChatMessageSnapshot]:
    if not raw:
        return []
    return [SelectedChatMessageSnapshot.model_validate(item) for item in raw]


def _to_paper_summary(paper: QuestionPaper) -> QuestionPaperSummary:
    versions = [
        QuestionPaperVersionSummary.model_validate(version)
        for version in (paper.versions or [])
    ]
    return QuestionPaperSummary(
        id=paper.id,
        notebook_id=paper.notebook_id,
        title=paper.title,
        created_at=paper.created_at,
        updated_at=paper.updated_at,
        versions=versions,
        latest_version=versions[-1] if versions else None,
    )


def _to_generation_result(
    paper: QuestionPaper,
    version: QuestionPaperVersion,
) -> GenerationResult:
    blueprint = QuestionPaperBlueprint.model_validate(version.blueprint)
    final_paper = resolve_final_paper(
        version.final_paper,
        version.generated_items,
    )
    paper_markdown = ""
    if version.status == QuestionPaperStatus.READY:
        paper_markdown = render_paper_markdown(blueprint, final_paper)
    return GenerationResult(
        paper_id=paper.id,
        version_id=version.id,
        notebook_id=paper.notebook_id,
        title=paper.title,
        version_number=version.version_number,
        status=version.status,
        blueprint=blueprint,
        final_paper=final_paper,
        generated_items=version.generated_items or [],
        paper_markdown=paper_markdown,
        selected_chat_messages=_parse_snapshots(version.selected_chat_messages),
        error=version.error,
    )


def _to_version_detail(
    paper: QuestionPaper,
    version: QuestionPaperVersion,
) -> QuestionPaperVersionDetail:
    result = _to_generation_result(paper, version)
    summary = QuestionPaperVersionSummary.model_validate(version)
    return QuestionPaperVersionDetail(
        **summary.model_dump(),
        question_paper_id=paper.id,
        notebook_id=paper.notebook_id,
        title=paper.title,
        blueprint=result.blueprint,
        final_paper=result.final_paper,
        generated_items=result.generated_items,
        selected_chapters=[
            SelectedChapter.model_validate(chapter)
            for chapter in (version.selected_chapters or [])
        ],
        selected_chat_messages=result.selected_chat_messages,
        teacher_instructions=version.teacher_instructions,
        generation_context=version.generation_context or {},
        generation_metadata=version.generation_metadata or {},
        paper_markdown=result.paper_markdown,
    )


async def get_owned_notebook(
    db: AsyncSession,
    notebook_id: UUID,
    user: User,
) -> Notebook | None:
    notebook = await db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != user.id or notebook.is_active is False:
        return None
    return notebook


async def get_owned_paper(
    db: AsyncSession,
    paper_id: UUID,
    user: User,
    *,
    load_versions: bool = False,
) -> QuestionPaper | None:
    if load_versions:
        result = await db.execute(
            select(QuestionPaper)
            .where(
                QuestionPaper.id == paper_id,
                QuestionPaper.is_active.is_(True),
            )
            .options(selectinload(QuestionPaper.versions))
        )
        paper = result.scalar_one_or_none()
    else:
        paper = await db.get(QuestionPaper, paper_id)
        if paper is not None and paper.is_active is False:
            paper = None
    if paper is None:
        return None
    notebook = await get_owned_notebook(db, paper.notebook_id, user)
    if notebook is None:
        return None
    return paper


async def list_papers_for_notebook(
    db: AsyncSession,
    notebook_id: UUID,
) -> list[QuestionPaper]:
    result = await db.execute(
        select(QuestionPaper)
        .where(
            QuestionPaper.notebook_id == notebook_id,
            QuestionPaper.is_active.is_(True),
        )
        .options(selectinload(QuestionPaper.versions))
        .order_by(QuestionPaper.updated_at.desc())
    )
    return list(result.scalars().unique().all())


async def soft_delete_paper(
    db: AsyncSession,
    paper_id: UUID,
    user: User,
) -> bool:
    paper = await get_owned_paper(db, paper_id, user)
    if paper is None:
        return False
    paper.is_active = False
    await db.commit()
    return True


async def _load_chat_message_snapshots(
    db: AsyncSession,
    *,
    notebook_id: UUID,
    user: User,
    message_ids: list[UUID],
) -> list[dict[str, Any]]:
    if not message_ids:
        return []

    unique_ids = list(dict.fromkeys(message_ids))
    result = await db.execute(
        select(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .join(Notebook, ChatSession.notebook_id == Notebook.id)
        .where(
            ChatMessage.id.in_(unique_ids),
            Notebook.id == notebook_id,
            Notebook.user_id == user.id,
            Notebook.is_active.is_(True),
        )
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
    )
    messages = list(result.scalars().all())
    found_ids = {message.id for message in messages}
    missing = [str(message_id) for message_id in unique_ids if message_id not in found_ids]
    if missing:
        raise LookupError(
            "One or more selected chat messages were not found in this notebook"
        )
    # Preserve caller order for reproducibility of selected context.
    by_id = {message.id: message for message in messages}
    ordered = [by_id[message_id] for message_id in unique_ids]
    return _snapshot_messages(ordered)


async def enqueue_paper_generation(
    db: AsyncSession,
    *,
    user: User,
    body: GeneratePaperRequest,
) -> GenerationResult:
    """Create a parent paper + pending Version 1 and enqueue Celery generation."""
    from app.tasks.generation import generate_question_paper_task

    notebook = await get_owned_notebook(db, body.notebook_id, user)
    if notebook is None:
        raise PermissionError("Notebook not found")

    title = _paper_title(body.blueprint, explicit=body.title)

    paper = QuestionPaper(
        notebook_id=notebook.id,
        title=title,
    )
    db.add(paper)
    await db.flush()

    version = QuestionPaperVersion(
        question_paper_id=paper.id,
        version_number=1,
        status=QuestionPaperStatus.PENDING,
        subject=body.subject,
        grade=body.grade,
        teacher_instructions=(body.teacher_instructions or "").strip() or None,
        selected_chapters=[c.model_dump(mode="json") for c in body.selected_chapters],
        blueprint=body.blueprint.model_dump(mode="json"),
        selected_chat_messages=[],
        generation_context={},
        generation_metadata={},
    )
    db.add(version)
    _touch_parent(paper)
    await db.commit()
    await db.refresh(paper)
    await db.refresh(version)

    generate_question_paper_task.delay(str(version.id))
    logger.info(
        "Enqueued question paper generation paper_id=%s version_id=%s",
        paper.id,
        version.id,
    )
    return _to_generation_result(paper, version)


async def enqueue_new_version(
    db: AsyncSession,
    *,
    user: User,
    paper_id: UUID,
    body: GenerateNewVersionRequest,
) -> GenerationResult:
    """Create the next version from the latest ready version + chat snapshots."""
    from app.tasks.generation import generate_next_question_paper_version_task

    result = await db.execute(
        select(QuestionPaper)
        .where(
            QuestionPaper.id == paper_id,
            QuestionPaper.is_active.is_(True),
        )
        .options(selectinload(QuestionPaper.versions))
        .with_for_update()
    )
    paper = result.scalar_one_or_none()
    if paper is None:
        raise PermissionError("Question paper not found")

    notebook = await get_owned_notebook(db, paper.notebook_id, user)
    if notebook is None:
        raise PermissionError("Question paper not found")

    versions = list(paper.versions or [])
    if any(version.status in ACTIVE_STATUSES for version in versions):
        raise ActiveGenerationError(
            "A generation is already pending or running for this paper"
        )

    ready_versions = [
        version
        for version in versions
        if version.status == QuestionPaperStatus.READY
    ]
    if not ready_versions:
        raise NoReadyVersionError(
            "No ready version exists to base a new revision on"
        )
    base = max(ready_versions, key=lambda version: version.version_number)
    next_number = (
        max(version.version_number for version in versions) + 1 if versions else 1
    )

    snapshots = await _load_chat_message_snapshots(
        db,
        notebook_id=paper.notebook_id,
        user=user,
        message_ids=body.selected_message_ids,
    )

    teacher_instructions = (body.teacher_instructions or "").strip() or None

    generation_context = {
        "base_version_id": str(base.id),
        "base_version_number": base.version_number,
        "base_final_paper": base.final_paper or {},
        "base_generated_items": base.generated_items or [],
        "selected_message_ids": [item["id"] for item in snapshots],
    }

    version = QuestionPaperVersion(
        question_paper_id=paper.id,
        version_number=next_number,
        status=QuestionPaperStatus.PENDING,
        subject=base.subject,
        grade=base.grade,
        teacher_instructions=teacher_instructions,
        selected_chapters=list(base.selected_chapters or []),
        blueprint=dict(base.blueprint or {}),
        # Seed prior paper so workers/UI can show base until generation completes.
        final_paper=dict(base.final_paper or {}),
        generated_items=list(base.generated_items or []),
        selected_chat_messages=snapshots,
        generation_context=generation_context,
        generation_metadata={},
        base_version_id=base.id,
    )
    db.add(version)
    _touch_parent(paper)
    await db.commit()
    await db.refresh(paper)
    await db.refresh(version)

    generate_next_question_paper_version_task.delay(str(version.id))
    logger.info(
        "Enqueued next-version generation paper_id=%s version_id=%s base=%s",
        paper.id,
        version.id,
        base.id,
    )
    return _to_generation_result(paper, version)


def run_paper_generation(version_id: UUID, *, db: Session | None = None) -> None:
    """Sync worker entrypoint: generate and persist results for one version."""

    def _run(session: Session) -> None:
        version = session.get(QuestionPaperVersion, version_id)
        if version is None:
            logger.warning("Version %s not found; skipping generation", version_id)
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

        started_at = datetime.now(UTC)
        version.status = QuestionPaperStatus.RUNNING
        version.error = None
        metadata = dict(version.generation_metadata or {})
        metadata.update(
            {
                "started_at": started_at.isoformat(),
                "worker": "celery",
                "task": "generate_question_paper",
            }
        )
        version.generation_metadata = metadata
        _touch_parent(paper)
        session.commit()

        try:
            if not version.selected_chapters:
                raise ValueError("selected_chapters is empty — cannot generate")

            blueprint = QuestionPaperBlueprint.model_validate(version.blueprint)
            selected_chapters = [
                SelectedChapter.model_validate(chapter)
                for chapter in version.selected_chapters
            ]

            result = generate_paper(
                blueprint=blueprint,
                selected_chapters=selected_chapters,
                subject=version.subject,
                grade=version.grade,
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
                    "duration_seconds": (
                        finished_at - started_at
                    ).total_seconds(),
                }
            )
            version.generation_metadata = metadata
            if not paper.title.strip():
                paper.title = _paper_title(result.blueprint)
            _touch_parent(paper)
            session.commit()
            logger.info("Version %s generation completed", version_id)
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
            logger.exception("Version %s generation failed", version_id)
            raise

    if db is not None:
        _run(db)
    else:
        with get_sync_db() as session:
            _run(session)


def fail_stuck_versions(
    *,
    timeout_minutes: int | None = None,
    db: Session | None = None,
) -> int:
    """Mark long-running versions as failed. Returns number of rows updated."""
    minutes = timeout_minutes or settings.generation_stuck_timeout_minutes
    cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

    def _run(session: Session) -> int:
        result = session.execute(
            select(QuestionPaperVersion)
            .where(
                QuestionPaperVersion.status == QuestionPaperStatus.RUNNING,
                QuestionPaperVersion.updated_at < cutoff,
            )
            .options(selectinload(QuestionPaperVersion.question_paper))
        )
        stuck = list(result.scalars().all())
        for version in stuck:
            version.status = QuestionPaperStatus.FAILED
            version.error = (
                f"Generation timed out after {minutes} minutes "
                "with no completion from the worker."
            )
            if version.question_paper is not None:
                _touch_parent(version.question_paper)
        if stuck:
            session.commit()
            logger.warning(
                "Marked %s stuck question paper version(s) as failed",
                len(stuck),
            )
        return len(stuck)

    if db is not None:
        return _run(db)
    with get_sync_db() as session:
        return _run(session)


async def get_paper_detail(
    db: AsyncSession,
    paper_id: UUID,
    user: User,
) -> QuestionPaperSummary | None:
    paper = await get_owned_paper(db, paper_id, user, load_versions=True)
    if paper is None:
        return None
    return _to_paper_summary(paper)


async def list_paper_summaries(
    db: AsyncSession,
    notebook_id: UUID,
) -> list[QuestionPaperSummary]:
    papers = await list_papers_for_notebook(db, notebook_id)
    return [_to_paper_summary(paper) for paper in papers]


async def get_owned_version(
    db: AsyncSession,
    *,
    paper_id: UUID,
    version_number: int,
    user: User,
) -> tuple[QuestionPaper, QuestionPaperVersion] | None:
    paper = await get_owned_paper(db, paper_id, user)
    if paper is None:
        return None
    result = await db.execute(
        select(QuestionPaperVersion).where(
            QuestionPaperVersion.question_paper_id == paper_id,
            QuestionPaperVersion.version_number == version_number,
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        return None
    return paper, version


async def get_version_detail(
    db: AsyncSession,
    *,
    paper_id: UUID,
    version_number: int,
    user: User,
) -> QuestionPaperVersionDetail | None:
    owned = await get_owned_version(
        db,
        paper_id=paper_id,
        version_number=version_number,
        user=user,
    )
    if owned is None:
        return None
    paper, version = owned
    return _to_version_detail(paper, version)
