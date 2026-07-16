from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
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
        color_hex=body.color_hex,
        selected_chapters=selected_chapters,
    )
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook
