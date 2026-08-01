from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi_pagination.ext.sqlalchemy import apaginate
from sse_starlette import EventSourceResponse

from app.api.deps import ChatServiceDep, CurrentUser, SessionDep
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionResponse,
    ChatTurnRequest,
)

router = APIRouter(prefix="/notebooks/{notebook_id}/chat", tags=["chat"])

ChatMessagePage = CustomizedPage[
    CursorPage[ChatMessageResponse],
    UseParamsFields(size=5),
]


@router.get("", response_model=ChatSessionResponse)
async def get_notebook_chat(
    notebook_id: UUID, current_user: CurrentUser, chat_service: ChatServiceDep
) -> ChatSessionResponse:
    return await chat_service.get_chat(notebook_id, current_user)


@router.get("/messages", response_model=ChatMessagePage)
async def list_notebook_chat_messages(
    notebook_id: UUID,
    current_user: CurrentUser,
    chat_service: ChatServiceDep,
    db: SessionDep,
) -> Any:
    """Cursor-paginated messages: DB fetches newest-first; items returned oldest→newest."""
    session = await chat_service.get_or_create_owned_session(notebook_id, current_user)
    query = chat_service.messages_cursor_query(session.id)

    def to_chronological(items: Sequence[Any]) -> Sequence[ChatMessageResponse]:
        return [ChatMessageResponse.model_validate(item) for item in reversed(items)]

    return await apaginate(db, query, transformer=to_chronological)


@router.post("/messages")
async def create_chat_turn(
    notebook_id: UUID,
    body: ChatTurnRequest,
    current_user: CurrentUser,
    chat_service: ChatServiceDep,
) -> EventSourceResponse:
    stream = await chat_service.start_turn(
        notebook_id=notebook_id,
        user=current_user,
        content=body.content,
        top_k=body.top_k,
        enabled_tools=body.enabled_tools,
    )
    return EventSourceResponse(stream)
