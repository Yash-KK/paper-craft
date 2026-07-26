from uuid import UUID

from fastapi import APIRouter, HTTPException, status
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


generation_router = APIRouter(prefix="/generation", tags=["generation"])


@generation_router.post("/papers", response_model=GenerationResult)
async def create_question_paper(
    body: GeneratePaperRequest,
    current_user: CurrentUser,
) -> GenerationResult:
    del current_user
    try:
        return generate_paper(
            blueprint=body.blueprint,
            selected_chapters=body.selected_chapters,
            subject=body.subject,
            grade=body.grade,
            teacher_instructions=body.teacher_instructions,
            use_sample_as_context=body.use_sample_as_context,
            sample_text=body.sample_text,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
