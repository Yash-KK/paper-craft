from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.notebook import ClassGrade, Subject


class NotebookChapterCreate(BaseModel):
    book_code: str = Field(max_length=50)
    chapter_number: int
    chapter_name: str = Field(max_length=255)
    subject: Subject | None = None
    grade: ClassGrade | None = None
    enabled: bool = True


class NotebookChapterUpdate(BaseModel):
    book_code: str | None = Field(default=None, max_length=50)
    chapter_number: int | None = None
    chapter_name: str | None = Field(default=None, max_length=255)
    subject: Subject | None = None
    grade: ClassGrade | None = None
    enabled: bool | None = None


class NotebookChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notebook_id: UUID
    book_code: str
    chapter_number: int
    chapter_name: str
    subject: Subject | None = None
    grade: ClassGrade | None = None
    enabled: bool
    created_at: datetime


class NotebookCreate(BaseModel):
    name: str = Field(max_length=255)
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = Field(default=None, max_length=10)


class NotebookUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = Field(default=None, max_length=10)


class NotebookListItem(BaseModel):
    """Basic notebook fields for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = None


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = None
    created_at: datetime
    updated_at: datetime
    chapters: list[NotebookChapterResponse] = Field(default_factory=list)
