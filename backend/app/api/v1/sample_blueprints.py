import json
import tempfile
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep
from app.db.models.sample_blueprint import SampleBlueprint
from app.schemas.generation import (
    GeneratePaperRequest,
    GenerationResult,
    QuestionPaperBlueprint,
    SampleBlueprintDetail,
    SampleBlueprintSummary,
)
from app.services.generation import generate_paper

router = APIRouter(prefix="/sample-blueprints", tags=["sample-blueprints"])
generation_router = APIRouter(prefix="/generation", tags=["generation"])


@router.get("", response_model=list[SampleBlueprintSummary])
async def list_sample_blueprints(
    current_user: CurrentUser,
    db: SessionDep,
) -> list[SampleBlueprint]:
    del current_user  # auth gate only
    result = await db.execute(
        select(SampleBlueprint)
        .where(SampleBlueprint.is_active.is_(True))
        .order_by(SampleBlueprint.sort_order.asc(), SampleBlueprint.label.asc())
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
    return SampleBlueprintDetail(
        id=row.id,
        slug=row.slug,
        label=row.label,
        total_marks=row.total_marks,
        blueprint=QuestionPaperBlueprint.model_validate(row.blueprint),
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
    del current_user
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

        return generate_paper(
            blueprint=body.blueprint,
            selected_chapters=body.selected_chapters,
            subject=body.subject,
            grade=body.grade,
            teacher_instructions=body.teacher_instructions,
            format_reference_path=uploaded_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
