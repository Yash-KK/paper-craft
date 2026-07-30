from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, SessionDep
from app.db.models.notebook import Board, Subject
from app.db.models.question_paper import QuestionPaperStatus
from app.db.models.sample_blueprint import SampleBlueprint
from app.schemas.generation import (
    GenerateNewVersionRequest,
    GeneratePaperRequest,
    GenerationResult,
    QuestionPaperSummary,
    QuestionPaperVersionDetail,
    SampleBlueprintDetail,
    SampleBlueprintSummary,
)
from app.services.documents import resolve_document
from app.services.export import (
    DOCX_MEDIA_TYPE,
    PandocNotFoundError,
    render_answer_key_docx_bytes,
    render_question_paper_docx_bytes,
)
from app.services.generation.papers import (
    ActiveGenerationError,
    NoReadyVersionError,
    enqueue_new_version,
    enqueue_paper_generation,
    get_owned_notebook,
    get_owned_version,
    get_paper_detail,
    get_version_detail,
    list_paper_summaries,
)

router = APIRouter(prefix="/sample-blueprints", tags=["sample-blueprints"])
generation_router = APIRouter(prefix="/generation", tags=["generation"])


@router.get("", response_model=list[SampleBlueprintSummary])
async def list_sample_blueprints(
    current_user: CurrentUser,
    db: SessionDep,
    board: Board | None = None,
    subject: Subject | None = None,
) -> list[SampleBlueprint]:
    del current_user  # auth gate only
    query = select(SampleBlueprint).where(SampleBlueprint.is_active.is_(True))

    if board is not None:
        query = query.where(
            or_(SampleBlueprint.board.is_(None), SampleBlueprint.board == board)
        )
    if subject is not None:
        query = query.where(
            or_(SampleBlueprint.subject.is_(None), SampleBlueprint.subject == subject)
        )
    result = await db.execute(
        query.order_by(SampleBlueprint.sort_order.asc(), SampleBlueprint.label.asc())
    )
    return list(result.scalars().all())


@router.get("/{blueprint_id}", response_model=SampleBlueprintDetail)
async def get_sample_blueprint(
    blueprint_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> SampleBlueprintDetail:
    del current_user
    row = await db.get(SampleBlueprint, blueprint_id)
    if row is None or not row.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample blueprint not found",
        )
    return SampleBlueprintDetail.model_validate(row)


@generation_router.post(
    "/papers",
    response_model=GenerationResult,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_question_paper(
    body: GeneratePaperRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> GenerationResult:
    try:
        return await enqueue_paper_generation(
            db,
            user=current_user,
            body=body,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@generation_router.post(
    "/papers/{paper_id}/versions",
    response_model=GenerationResult,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_question_paper_version(
    paper_id: UUID,
    body: GenerateNewVersionRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> GenerationResult:
    try:
        return await enqueue_new_version(
            db,
            user=current_user,
            paper_id=paper_id,
            body=body,
        )
    except (PermissionError, LookupError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (ActiveGenerationError, NoReadyVersionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@generation_router.get(
    "/notebooks/{notebook_id}/papers",
    response_model=list[QuestionPaperSummary],
)
async def list_notebook_papers(
    notebook_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> list[QuestionPaperSummary]:
    notebook = await get_owned_notebook(db, notebook_id, current_user)
    if notebook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    return await list_paper_summaries(db, notebook_id)


@generation_router.get("/papers/{paper_id}", response_model=QuestionPaperSummary)
async def get_question_paper(
    paper_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> QuestionPaperSummary:
    detail = await get_paper_detail(db, paper_id, current_user)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper not found",
        )
    return detail


@generation_router.get(
    "/papers/{paper_id}/versions/{version_number}",
    response_model=QuestionPaperVersionDetail,
)
async def get_question_paper_version(
    paper_id: UUID,
    version_number: int,
    current_user: CurrentUser,
    db: SessionDep,
) -> QuestionPaperVersionDetail:
    detail = await get_version_detail(
        db,
        paper_id=paper_id,
        version_number=version_number,
        user=current_user,
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper version not found",
        )
    return detail


@generation_router.get("/papers/{paper_id}/versions/{version_number}/export")
async def export_question_paper_version(
    paper_id: UUID,
    version_number: int,
    current_user: CurrentUser,
    db: SessionDep,
    variant: Literal["paper", "answer_key"] = "paper",
) -> Response:
    owned = await get_owned_version(
        db,
        paper_id=paper_id,
        version_number=version_number,
        user=current_user,
    )
    if owned is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper version not found",
        )
    paper, version = owned
    if version.status != QuestionPaperStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Version is not ready for export "
                f"(status={version.status.value})"
            ),
        )

    try:
        template = resolve_document()
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        if variant == "answer_key":
            content = render_answer_key_docx_bytes(
                version.blueprint,
                version.final_answer_key,
                template,
            )
            filename = (
                f"{_safe_filename(paper.title)}-v{version.version_number}"
                "-answer-key.docx"
            )
        else:
            content = render_question_paper_docx_bytes(
                version.blueprint,
                version.final_paper,
                template,
            )
            filename = (
                f"{_safe_filename(paper.title)}-v{version.version_number}.docx"
            )
    except PandocNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build DOCX: {exc}",
        ) from exc

    return StreamingResponse(
        iter([content]),
        media_type=DOCX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


def _safe_filename(title: str) -> str:
    cleaned = "".join(
        ch if ch.isalnum() or ch in ("-", "_", " ") else "-" for ch in title
    )
    cleaned = "-".join(cleaned.split()) or "question-paper"
    return cleaned[:80]
