from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep
from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import ClassGrade, Subject
from app.schemas.notebook import ChapterCatalogItem

router = APIRouter(prefix="/chapters", tags=["chapters"])


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
