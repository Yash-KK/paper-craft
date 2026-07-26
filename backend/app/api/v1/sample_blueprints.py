import json
import tempfile
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, SessionDep
from app.db.models.notebook import Board, Subject
from app.db.models.question_paper import QuestionPaperStatus
from app.db.models.sample_blueprint import SampleBlueprint
from app.schemas.generation import (
    GeneratePaperRequest,
    GenerationResult,
    QuestionPaperDetail,
    QuestionPaperSummary,
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
    create_and_generate_paper,
    get_owned_notebook,
    get_owned_paper,
    get_paper_detail,
    list_papers_for_notebook,
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
    return SampleBlueprintDetail.model_validate(
        {
            "id": row.id,
            "slug": row.slug,
            "label": row.label,
            "kind": row.kind,
            "total_marks": row.total_marks,
            "board": row.board,
            "subject": row.subject,
            "grade": row.grade,
            "format_reference_uri": row.format_reference_uri,
            "blueprint": row.blueprint,
        }
    )


async def _save_format_reference(upload: UploadFile) -> Path:
    filename = (upload.filename or "").lower()
    if not filename.endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format reference must be a .docx file",
        )

    content = await upload.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded format reference is empty",
        )

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(content)
        return tmp_path.resolve()
    except Exception as exc:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format reference: {exc}",
        ) from exc


@generation_router.post("/papers", response_model=GenerationResult)
async def create_question_paper(
    current_user: CurrentUser,
    db: SessionDep,
    payload: Annotated[
        str, Form(description="JSON GeneratePaperRequest body")
    ],
    format_reference: Annotated[
        UploadFile | None,
        File(
            description="Optional DOCX used as the formatting template for the final paper",
        ),
    ] = None,
) -> GenerationResult:
    try:
        body = GeneratePaperRequest.model_validate(json.loads(payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload JSON: {exc}",
        ) from exc

    uploaded_path: Path | None = None
    try:
        if format_reference is not None and format_reference.filename:
            uploaded_path = await _save_format_reference(format_reference)

        return await create_and_generate_paper(
            db,
            user=current_user,
            body=body,
            format_reference_upload=uploaded_path,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (ValueError, NotImplementedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        if uploaded_path is not None:
            uploaded_path.unlink(missing_ok=True)


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
    papers = await list_papers_for_notebook(db, notebook_id)
    return [QuestionPaperSummary.model_validate(paper) for paper in papers]


@generation_router.get("/papers/{paper_id}", response_model=QuestionPaperDetail)
async def get_question_paper(
    paper_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> QuestionPaperDetail:
    detail = await get_paper_detail(db, paper_id, current_user)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper not found",
        )
    return detail


@generation_router.get("/papers/{paper_id}/export")
async def export_question_paper(
    paper_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
    variant: Literal["paper", "answer_key"] = "paper",
) -> Response:
    paper = await get_owned_paper(db, paper_id, current_user)
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper not found",
        )
    if paper.status != QuestionPaperStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Paper is not ready for export (status={paper.status.value})",
        )

    try:
        reference = resolve_document(paper.format_reference_uri)
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        if variant == "answer_key":
            content = render_answer_key_docx_bytes(
                paper.blueprint,
                paper.final_answer_key,
                reference,
            )
            filename = f"{_safe_filename(paper.title)}-answer-key.docx"
        else:
            content = render_question_paper_docx_bytes(
                paper.blueprint,
                paper.final_paper,
                reference,
            )
            filename = f"{_safe_filename(paper.title)}.docx"
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
