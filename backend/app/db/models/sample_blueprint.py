import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.notebook import Board, ClassGrade, Subject
from app.schemas.generation import BlueprintKind


class SampleBlueprint(Base):
    __tablename__ = "sample_blueprints"
    __table_args__ = (
        Index(
            "ix_sample_blueprints_active_board_subject",
            "is_active",
            "board",
            "subject",
            "sort_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[BlueprintKind] = mapped_column(
        Enum(BlueprintKind, name="sample_blueprint_kind", native_enum=False, length=40),
        nullable=False,
        default=BlueprintKind.EXAM,
    )
    total_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    board: Mapped[Board | None] = mapped_column(
        Enum(Board, name="sample_blueprint_board", native_enum=False, length=20),
        nullable=True,
    )
    grade: Mapped[ClassGrade | None] = mapped_column(
        Enum(ClassGrade, name="sample_blueprint_grade", native_enum=False, length=50),
        nullable=True,
    )
    subject: Mapped[Subject | None] = mapped_column(
        Enum(Subject, name="sample_blueprint_subject", native_enum=False, length=100),
        nullable=True,
    )
    format_reference_uri: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="Document URI for the formatting sample (local:... or future s3://...).",
    )
    blueprint: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
