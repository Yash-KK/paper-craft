import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.chat import ChatSession
    from app.db.models.user import User


class ClassGrade(str, enum.Enum):
    CLASS_9 = "Class 9"
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
    selected_chapters: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, nullable=False
    )
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
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="notebook",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "uq_notebooks_user_name_ci",
            user_id,
            func.lower(func.btrim(name)),
            unique=True,
        ),
    )
