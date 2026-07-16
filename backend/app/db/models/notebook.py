import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class ClassGrade(str, enum.Enum):
    CLASS_10 = "Class 10"


class Subject(str, enum.Enum):
    MATHEMATICS = "Mathematics"


class Notebook(Base):
    __tablename__ = "notebooks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    class_grade: Mapped[ClassGrade | None] = mapped_column(
        Enum(ClassGrade, name="class_grade", native_enum=False, length=50),
        nullable=True,
    )
    subject: Mapped[Subject | None] = mapped_column(
        Enum(Subject, name="subject", native_enum=False, length=100),
        nullable=True,
    )
    color_hex: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="notebooks")
    chapters: Mapped[list["NotebookChapter"]] = relationship(
        back_populates="notebook",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class NotebookChapter(Base):
    __tablename__ = "notebook_chapters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notebooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    book_code: Mapped[str] = mapped_column(String(50), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Subject | None] = mapped_column(
        Enum(Subject, name="notebook_chapter_subject", native_enum=False, length=100),
        nullable=True,
    )
    grade: Mapped[ClassGrade | None] = mapped_column(
        Enum(ClassGrade, name="notebook_chapter_grade", native_enum=False, length=50),
        nullable=True,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    notebook: Mapped["Notebook"] = relationship(back_populates="chapters")
