import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.db.models.chat import ChatMessage, ChatMessageRole, ChatSession
from app.db.models.notebook import Notebook
from app.schemas.chat import ChatMessageResponse, ChatSessionDetail, ChatTurnRequest
from app.services.chat import stream_notebook_chat

router = APIRouter(prefix="/notebooks/{notebook_id}/chat", tags=["chat"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


async def _get_owned_notebook(
    notebook_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> Notebook:
    notebook = await db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    return notebook


async def _get_or_create_session(
    notebook: Notebook,
    db: SessionDep,
) -> ChatSession:
    session = await db.scalar(
        select(ChatSession).where(ChatSession.notebook_id == notebook.id)
    )
    if session is not None:
        return session

    session = ChatSession(
        notebook_id=notebook.id,
        title=notebook.name,
    )
    db.add(session)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        existing_session = await db.scalar(
            select(ChatSession).where(ChatSession.notebook_id == notebook.id)
        )
        if existing_session is None:
            raise
        return existing_session

    await db.refresh(session)
    return session


async def _get_messages(
    session_id: UUID,
    db: SessionDep,
) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
    )
    return list(result.scalars().all())


@router.get("", response_model=ChatSessionDetail)
async def get_notebook_chat(
    notebook_id: UUID,
    current_user: CurrentUser,
    db: SessionDep,
) -> ChatSessionDetail:
    notebook = await _get_owned_notebook(notebook_id, current_user, db)
    session = await _get_or_create_session(notebook, db)
    messages = await _get_messages(session.id, db)

    return ChatSessionDetail(
        id=session.id,
        notebook_id=session.notebook_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            ChatMessageResponse.model_validate(message) for message in messages
        ],
    )


@router.post("/messages")
async def create_chat_turn(
    notebook_id: UUID,
    body: ChatTurnRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> StreamingResponse:
    notebook = await _get_owned_notebook(notebook_id, current_user, db)
    session = await _get_or_create_session(notebook, db)
    history = await _get_messages(session.id, db)

    user_message = ChatMessage(
        session_id=session.id,
        role=ChatMessageRole.USER,
        content=body.content,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    user_payload = ChatMessageResponse.model_validate(user_message).model_dump(
        mode="json"
    )
    selected_chapters = list(notebook.selected_chapters)
    session_id = session.id
    question = body.content
    top_k = body.top_k

    async def generate() -> AsyncIterator[str]:
        try:
            async for event in stream_notebook_chat(
                question=question,
                history=history,
                selected_chapters=selected_chapters,
                top_k=top_k,
            ):
                event_type = event.get("type")

                if event_type == "complete":
                    answer = event.get("answer") or ""
                    if not answer:
                        yield _sse(
                            {
                                "type": "error",
                                "message": (
                                    "The chat service could not generate a response"
                                ),
                            }
                        )
                        return

                    assistant_message = ChatMessage(
                        session_id=session_id,
                        role=ChatMessageRole.ASSISTANT,
                        content=answer,
                        message_metadata={
                            "tool_calls": event.get("tool_calls") or [],
                        },
                    )
                    chat_session = await db.get(ChatSession, session_id)
                    if chat_session is not None:
                        chat_session.updated_at = datetime.now(timezone.utc)
                    db.add(assistant_message)
                    await db.commit()
                    await db.refresh(assistant_message)

                    yield _sse(
                        {
                            "type": "done",
                            "session_id": str(session_id),
                            "user_message": user_payload,
                            "assistant_message": ChatMessageResponse.model_validate(
                                assistant_message
                            ).model_dump(mode="json"),
                        }
                    )
                    return

                if event_type == "error":
                    yield _sse(
                        {
                            "type": "error",
                            "message": event.get("message")
                            or "The chat service could not generate a response",
                        }
                    )
                    return

                yield _sse(event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
