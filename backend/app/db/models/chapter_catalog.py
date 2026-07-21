import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.notebook import ClassGrade, Subject


class ChapterCatalog(Base):
    __tablename__ = "chapter_catalog"
    __table_args__ = (
        UniqueConstraint("book_code", "chapter_number", name="uq_chapter_catalog_book_chapter"),
        Index("ix_chapter_catalog_grade_subject", "grade", "subject"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    book_code: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[Subject] = mapped_column(
        Enum(Subject, name="chapter_catalog_subject", native_enum=False, length=100),
        nullable=False,
    )
    grade: Mapped[ClassGrade] = mapped_column(
        Enum(ClassGrade, name="chapter_catalog_grade", native_enum=False, length=50),
        nullable=False,
    )
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
