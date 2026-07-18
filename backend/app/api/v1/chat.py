from uuid import UUID

from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from app.api.deps import ChatServiceDep, CurrentUser
from app.schemas.chat import ChatSessionDetail, ChatTurnRequest

router = APIRouter(prefix="/notebooks/{notebook_id}/chat", tags=["chat"])


@router.get("", response_model=ChatSessionDetail)
async def get_notebook_chat(
    notebook_id: UUID, current_user: CurrentUser, chat_service: ChatServiceDep
) -> ChatSessionDetail:
    return await chat_service.get_chat(notebook_id, current_user)


@router.post("/messages")
async def create_chat_turn(
    notebook_id: UUID, body: ChatTurnRequest, current_user: CurrentUser, chat_service: ChatServiceDep
) -> EventSourceResponse:
    stream = await chat_service.start_turn(
        notebook_id=notebook_id, user=current_user, content=body.content, top_k=body.top_k
    )
    return EventSourceResponse(stream)