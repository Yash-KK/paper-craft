from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import Board, ClassGrade, Subject
from app.schemas.notebook import ChapterCatalogItem

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/boards", response_model=list[Board])
async def list_boards() -> list[Board]:
    return list(Board)


@router.get("/grades", response_model=list[ClassGrade])
async def list_grades(board: Board, db: SessionDep) -> list[ClassGrade]:
    result = await db.execute(
        select(ChapterCatalog.grade)
        .where(ChapterCatalog.board == board)
        .distinct()
        .order_by(ChapterCatalog.grade)
    )
    return list(result.scalars().all())


@router.get("/subjects", response_model=list[Subject])
async def list_subjects(
    board: Board,
    grade: ClassGrade,
    db: SessionDep,
) -> list[Subject]:
    result = await db.execute(
        select(ChapterCatalog.subject)
        .where(
            ChapterCatalog.board == board,
            ChapterCatalog.grade == grade,
        )
        .distinct()
        .order_by(ChapterCatalog.subject)
    )
    return list(result.scalars().all())


@router.get("", response_model=list[ChapterCatalogItem])
async def list_chapters(
    board: Board,
    grade: ClassGrade,
    subject: Subject,
    db: SessionDep,
) -> list[ChapterCatalog]:
    result = await db.execute(
        select(ChapterCatalog)
        .where(
            ChapterCatalog.board == board,
            ChapterCatalog.grade == grade,
            ChapterCatalog.subject == subject,
        )
        .order_by(ChapterCatalog.chapter_number)
    )
    return list(result.scalars().all())


@router.patch("/availability", response_model=ChapterCatalogItem)
async def set_chapter_availability(
    board: Board,
    grade: ClassGrade,
    subject: Subject,
    chapter_number: int,
    is_available: bool,
    db: SessionDep,
) -> ChapterCatalog:
    result = await db.execute(
        select(ChapterCatalog).where(
            ChapterCatalog.board == board,
            ChapterCatalog.grade == grade,
            ChapterCatalog.subject == subject,
            ChapterCatalog.chapter_number == chapter_number,
        )
    )
    chapter = result.scalar_one_or_none()
    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )

    chapter.is_available = is_available
    await db.commit()
    await db.refresh(chapter)
    return chapter
