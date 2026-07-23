import random
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import ClassGrade, Notebook, Subject
from app.schemas.notebook import NotebookCreate, NotebookListItem, NotebookUpdate

router = APIRouter(prefix="/notebooks", tags=["notebooks"])

NOTEBOOK_COLORS = (
    "#7c3aed",
    "#14b8a6",
    "#f59e0b",
    "#ec4899",
    "#22c55e",
    "#d946ef",
)


async def _resolve_selected_chapters(
    db: SessionDep,
    *,
    class_grade: ClassGrade,
    subject: Subject,
    chapter_numbers: list[int],
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(ChapterCatalog).where(
            ChapterCatalog.grade == class_grade,
            ChapterCatalog.subject == subject,
            ChapterCatalog.is_available.is_(True),
            ChapterCatalog.chapter_number.in_(chapter_numbers),
        )
    )
    fetched_chapters = list(result.scalars().all())

    if len(fetched_chapters) != len(set(chapter_numbers)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chapter selection",
        )

    return [
        {
            "book_code": ch.book_code,
            "chapter_number": ch.chapter_number,
            "chapter_name": ch.chapter_name,
        }
        for ch in sorted(fetched_chapters, key=lambda c: c.chapter_number)
    ]


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

    selected_chapters = await _resolve_selected_chapters(
        db,
        class_grade=body.class_grade,
        subject=body.subject,
        chapter_numbers=body.selected_chapter_numbers,
    )

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


@router.patch("/{notebook_id}", response_model=NotebookListItem)
async def update_notebook(
    notebook_id: UUID,
    body: NotebookUpdate,
    current_user: CurrentUser,
    db: SessionDep,
) -> Notebook:
    notebook = await db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )

    if body.name is not None:
        name = body.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notebook name cannot be blank",
            )
        existing_id = await db.scalar(
            select(Notebook.id).where(
                Notebook.user_id == current_user.id,
                Notebook.id != notebook_id,
                func.lower(func.btrim(Notebook.name)) == name.lower(),
            )
        )
        if existing_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A notebook with this name already exists",
            )
        notebook.name = name

    if body.class_grade is not None:
        notebook.class_grade = body.class_grade
    if body.subject is not None:
        notebook.subject = body.subject
    if body.color_hex is not None:
        notebook.color_hex = body.color_hex

    if body.selected_chapter_numbers is not None:
        if notebook.class_grade is None or notebook.subject is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notebook class and subject are required to update chapters",
            )
        notebook.selected_chapters = await _resolve_selected_chapters(
            db,
            class_grade=notebook.class_grade,
            subject=notebook.subject,
            chapter_numbers=body.selected_chapter_numbers,
        )

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
