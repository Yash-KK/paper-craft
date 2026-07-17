from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.chat import ChatMessageRole


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


class ChatStreamThinkingEvent(BaseModel):
    type: Literal["thinking"] = "thinking"


class ChatStreamTokenEvent(BaseModel):
    type: Literal["token"] = "token"
    content: str


class ChatStreamToolStartEvent(BaseModel):
    type: Literal["tool_start"] = "tool_start"
    tool: str
    input: str


class ChatStreamToolEndEvent(BaseModel):
    type: Literal["tool_end"] = "tool_end"
    tool: str
    output: str


class ChatStreamDoneEvent(BaseModel):
    type: Literal["done"] = "done"
    session_id: UUID
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


class ChatStreamErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str
