from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.chat import ChatMessageRole


class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ChatSessionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ChatMessageCreate(BaseModel):
    role: ChatMessageRole
    content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatTurnRequest(BaseModel):
    content: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("Message cannot be blank")
        return content


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    session_id: UUID
    role: ChatMessageRole
    content: str
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="message_metadata",
    )
    created_at: datetime


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notebook_id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class ChatSessionDetail(ChatSessionResponse):
    messages: list[ChatMessageResponse] = Field(default_factory=list)


class ChatTurnResponse(BaseModel):
    session_id: UUID
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
