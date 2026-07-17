from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.notebook import ClassGrade, Subject


class SelectedChapter(BaseModel):
    book_code: str
    chapter_number: int
    chapter_name: str


class ChapterCatalogItem(BaseModel):
    """Dropdown item returned by GET /chapters."""

    model_config = ConfigDict(from_attributes=True)

    chapter_number: int
    chapter_name: str
    book_code: str


class NotebookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    class_grade: ClassGrade
    subject: Subject
    selected_chapter_numbers: list[int] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Notebook name cannot be blank")
        return name


class NotebookUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = Field(default=None, max_length=10)
    selected_chapter_numbers: list[int] | None = Field(default=None, min_length=1)


class NotebookListItem(BaseModel):
    """Basic notebook fields for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = None
    selected_chapters: list[SelectedChapter] = Field(default_factory=list)
    updated_at: datetime


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    class_grade: ClassGrade | None = None
    subject: Subject | None = None
    color_hex: str | None = None
    selected_chapters: list[SelectedChapter] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
