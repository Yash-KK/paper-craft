from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import ClassGrade, Subject
from app.schemas.notebook import ChapterCatalogItem

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/grades", response_model=list[ClassGrade])
async def list_grades(db: SessionDep) -> list[ClassGrade]:
    result = await db.execute(
        select(ChapterCatalog.grade).distinct().order_by(ChapterCatalog.grade)
    )
    return list(result.scalars().all())


@router.get("/subjects", response_model=list[Subject])
async def list_subjects(
    grade: ClassGrade,
    db: SessionDep,
) -> list[Subject]:
    result = await db.execute(
        select(ChapterCatalog.subject)
        .where(ChapterCatalog.grade == grade)
        .distinct()
        .order_by(ChapterCatalog.subject)
    )
    return list(result.scalars().all())


@router.get("", response_model=list[ChapterCatalogItem])
async def list_chapters(
    grade: ClassGrade,
    subject: Subject,
    db: SessionDep,
) -> list[ChapterCatalog]:
    result = await db.execute(
        select(ChapterCatalog)
        .where(
            ChapterCatalog.grade == grade,
            ChapterCatalog.subject == subject,
        )
        .order_by(ChapterCatalog.chapter_number)
    )
    return list(result.scalars().all())
