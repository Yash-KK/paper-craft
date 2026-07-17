from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.db.models.chat import ChatMessage, ChatMessageRole, ChatSession
from app.db.models.notebook import Notebook
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionDetail,
    ChatTurnRequest,
    ChatTurnResponse,
)
from app.services.chat import generate_rag_response

router = APIRouter(prefix="/notebooks/{notebook_id}/chat", tags=["chat"])


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


@router.post(
    "/messages",
    response_model=ChatTurnResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_turn(
    notebook_id: UUID,
    body: ChatTurnRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> ChatTurnResponse:
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

    try:
        answer, citations = await generate_rag_response(
            question=body.content,
            history=history,
            selected_chapters=notebook.selected_chapters,
            top_k=body.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The chat service could not generate a response",
        ) from exc

    assistant_message = ChatMessage(
        session_id=session.id,
        role=ChatMessageRole.ASSISTANT,
        content=answer,
        message_metadata={"citations": citations},
    )
    session.updated_at = datetime.now(timezone.utc)
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return ChatTurnResponse(
        session_id=session.id,
        user_message=ChatMessageResponse.model_validate(user_message),
        assistant_message=ChatMessageResponse.model_validate(assistant_message),
    )
