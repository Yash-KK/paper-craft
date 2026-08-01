import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.notebook import Notebook


class QuestionPaperStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"


class QuestionPaper(Base):
    """Stable parent paper that groups one or more generation versions."""

    __tablename__ = "question_papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notebooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
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

    notebook: Mapped["Notebook"] = relationship(back_populates="question_papers")
    versions: Mapped[list["QuestionPaperVersion"]] = relationship(
        back_populates="question_paper",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="QuestionPaperVersion.version_number",
    )

    __table_args__ = (
        Index(
            "ix_question_papers_notebook_updated",
            notebook_id,
            updated_at,
            postgresql_where=text("is_active IS TRUE"),
        ),
    )


class QuestionPaperVersion(Base):
    """One generated (or in-progress) version of a question paper."""

    __tablename__ = "question_paper_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question_paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_papers.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[QuestionPaperStatus] = mapped_column(
        Enum(
            QuestionPaperStatus,
            name="question_paper_status",
            native_enum=False,
            length=20,
            create_constraint=True,
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
        default=QuestionPaperStatus.PENDING,
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    teacher_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_chapters: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    blueprint: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    final_paper: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    generated_items: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    selected_chat_messages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    generation_context: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    generation_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    base_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_paper_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    question_paper: Mapped[QuestionPaper] = relationship(back_populates="versions")
    base_version: Mapped["QuestionPaperVersion | None"] = relationship(
        remote_side=[id],
        foreign_keys=[base_version_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "question_paper_id",
            "version_number",
            name="uq_question_paper_versions_paper_number",
        ),
        Index(
            "ix_question_paper_versions_paper_updated",
            question_paper_id,
            updated_at,
        ),
        Index(
            "ix_question_paper_versions_paper_status",
            question_paper_id,
            status,
        ),
    )
