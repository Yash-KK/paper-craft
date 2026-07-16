from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep
from app.db.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookListItem

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookListItem])
async def list_notebooks(
    current_user: CurrentUser,
    db: SessionDep,
) -> list[Notebook]:
    result = await db.execute(
        select(Notebook)
        .where(Notebook.user_id == current_user.id)
        .order_by(Notebook.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=NotebookListItem, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    body: NotebookCreate,
    current_user: CurrentUser,
    db: SessionDep,
) -> Notebook:
    notebook = Notebook(
        user_id=current_user.id,
        name=body.name,
        class_grade=body.class_grade,
        subject=body.subject,
        color_hex=body.color_hex,
    )
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook
