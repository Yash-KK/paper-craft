import random
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookListItem

router = APIRouter(prefix="/notebooks", tags=["notebooks"])

NOTEBOOK_COLORS = (
    "#7c3aed",
    "#14b8a6",
    "#f59e0b",
    "#ec4899",
    "#22c55e",
    "#d946ef",
)


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
    existing_id = await db.scalar(
        select(Notebook.id).where(
            Notebook.user_id == current_user.id,
            func.lower(func.btrim(Notebook.name)) == body.name.lower(),
        )
    )
    if existing_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A notebook with this name already exists",
        )

    result = await db.execute(
        select(ChapterCatalog).where(
            ChapterCatalog.grade == body.class_grade,
            ChapterCatalog.subject == body.subject,
            ChapterCatalog.chapter_number.in_(body.selected_chapter_numbers),
        )
    )
    fetched_chapters = list(result.scalars().all())

    if len(fetched_chapters) != len(set(body.selected_chapter_numbers)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chapter selection",
        )

    selected_chapters = [
        {
            "book_code": ch.book_code,
            "chapter_number": ch.chapter_number,
            "chapter_name": ch.chapter_name,
        }
        for ch in sorted(fetched_chapters, key=lambda c: c.chapter_number)
    ]

    notebook = Notebook(
        user_id=current_user.id,
        name=body.name,
        class_grade=body.class_grade,
        subject=body.subject,
        color_hex=random.choice(NOTEBOOK_COLORS),
        selected_chapters=selected_chapters,
    )
    db.add(notebook)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A notebook with this name already exists",
        ) from exc

    await db.refresh(notebook)
    return notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> None:
    notebook = await db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    await db.delete(notebook)
    await db.commit()
