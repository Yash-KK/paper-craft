"""Persist and load generated question papers."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import PROJECT_ROOT
from app.db.models.notebook import Notebook
from app.db.models.question_paper import QuestionPaper, QuestionPaperStatus
from app.db.models.user import User
from app.schemas.generation import (
    GeneratePaperRequest,
    GenerationResult,
    QuestionPaperBlueprint,
    QuestionPaperDetail,
)
from app.services.documents import to_local_uri
from app.services.export import (
    render_answer_key_markdown,
    render_paper_markdown,
)
from app.services.generation.service import generate_paper

FORMAT_REFERENCE_DIR = PROJECT_ROOT / "data" / "format_references"


def _paper_title(blueprint: QuestionPaperBlueprint) -> str:
    title = (blueprint.exam_title or "").strip()
    return title or "Question Paper"


def _persist_format_reference_upload(upload_path: Path) -> str:
    FORMAT_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    dest = FORMAT_REFERENCE_DIR / f"{uuid.uuid4()}.docx"
    shutil.copy2(upload_path, dest)
    return to_local_uri(f"data/format_references/{dest.name}")


def _to_generation_result(paper: QuestionPaper) -> GenerationResult:
    blueprint = QuestionPaperBlueprint.model_validate(paper.blueprint)
    return GenerationResult(
        id=paper.id,
        notebook_id=paper.notebook_id,
        title=paper.title,
        status=paper.status,
        version=paper.version,
        blueprint=blueprint,
        final_paper=paper.final_paper or {"sections": {}},
        final_answer_key=paper.final_answer_key or {"sections": {}},
        generated_items=paper.generated_items or [],
        format_reference_uri=paper.format_reference_uri,
        format_reference_is_default=paper.format_reference_is_default,
        paper_markdown=render_paper_markdown(blueprint, paper.final_paper or {}),
        answer_key_markdown=render_answer_key_markdown(
            blueprint, paper.final_answer_key or {}
        ),
        error=paper.error,
    )


def _to_detail(paper: QuestionPaper) -> QuestionPaperDetail:
    result = _to_generation_result(paper)
    return QuestionPaperDetail(
        id=paper.id,
        notebook_id=paper.notebook_id,
        title=paper.title,
        status=paper.status,
        version=paper.version,
        subject=paper.subject,
        grade=paper.grade,
        format_reference_uri=paper.format_reference_uri,
        format_reference_is_default=paper.format_reference_is_default,
        created_at=paper.created_at,
        updated_at=paper.updated_at,
        error=paper.error,
        blueprint=result.blueprint,
        final_paper=result.final_paper,
        final_answer_key=result.final_answer_key,
        generated_items=result.generated_items,
        teacher_instructions=paper.teacher_instructions,
        paper_markdown=result.paper_markdown,
        answer_key_markdown=result.answer_key_markdown,
    )


async def get_owned_notebook(
    db: AsyncSession,
    notebook_id: UUID,
    user: User,
) -> Notebook | None:
    notebook = await db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != user.id:
        return None
    return notebook


async def get_owned_paper(
    db: AsyncSession,
    paper_id: UUID,
    user: User,
) -> QuestionPaper | None:
    paper = await db.get(QuestionPaper, paper_id)
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
        .where(QuestionPaper.notebook_id == notebook_id)
        .order_by(QuestionPaper.updated_at.desc())
    )
    return list(result.scalars().all())


async def create_and_generate_paper(
    db: AsyncSession,
    *,
    user: User,
    body: GeneratePaperRequest,
    format_reference_upload: Path | None = None,
) -> GenerationResult:
    notebook = await get_owned_notebook(db, body.notebook_id, user)
    if notebook is None:
        raise PermissionError("Notebook not found")

    upload_uri: str | None = None
    if format_reference_upload is not None:
        upload_uri = _persist_format_reference_upload(format_reference_upload)

    paper = QuestionPaper(
        notebook_id=notebook.id,
        title=_paper_title(body.blueprint),
        status=QuestionPaperStatus.RUNNING,
        version=1,
        subject=body.subject,
        grade=body.grade,
        teacher_instructions=(body.teacher_instructions or "").strip() or None,
        blueprint=body.blueprint.model_dump(mode="json"),
        format_reference_uri=upload_uri
        or body.format_reference_uri
        or "local:samples/40_marks_sample.docx",
        format_reference_is_default=upload_uri is None
        and not (body.format_reference_uri or "").strip(),
    )
    db.add(paper)
    await db.flush()

    try:
        result = generate_paper(
            blueprint=body.blueprint,
            selected_chapters=body.selected_chapters,
            subject=body.subject,
            grade=body.grade,
            teacher_instructions=body.teacher_instructions,
            format_reference_uri=upload_uri or body.format_reference_uri,
            format_reference_upload=None,
        )
        result_uri = upload_uri or result.format_reference_uri
        is_default = (
            upload_uri is None and result.format_reference_is_default
        )
        paper.title = _paper_title(result.blueprint)
        paper.status = QuestionPaperStatus.READY
        paper.blueprint = result.blueprint.model_dump(mode="json")
        paper.final_paper = result.final_paper
        paper.final_answer_key = result.final_answer_key
        paper.generated_items = result.generated_items
        paper.format_reference_uri = result_uri
        paper.format_reference_is_default = is_default
        paper.error = None
        await db.commit()
        await db.refresh(paper)
        return _to_generation_result(paper)
    except Exception as exc:
        paper.status = QuestionPaperStatus.FAILED
        paper.error = str(exc)
        await db.commit()
        raise


async def get_paper_detail(
    db: AsyncSession,
    paper_id: UUID,
    user: User,
) -> QuestionPaperDetail | None:
    paper = await get_owned_paper(db, paper_id, user)
    if paper is None:
        return None
    return _to_detail(paper)
