from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat import ChatMessage, ChatMessageRole, ChatSession
from app.db.models.notebook import Notebook
from app.db.models.user import User


class ChatRepository:
    """Persistence helpers for notebook chat sessions and messages."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_owned_notebook(
        self,
        notebook_id: UUID,
        user: User,
    ) -> Notebook | None:
        notebook = await self._db.get(Notebook, notebook_id)
        if notebook is None or notebook.user_id != user.id:
            return None
        return notebook

    async def get_or_create_session(self, notebook: Notebook) -> ChatSession:
        session = await self._db.scalar(
            select(ChatSession).where(ChatSession.notebook_id == notebook.id)
        )
        if session is not None:
            return session

        session = ChatSession(
            notebook_id=notebook.id,
            title=notebook.name,
        )
        self._db.add(session)
        try:
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            existing = await self._db.scalar(
                select(ChatSession).where(ChatSession.notebook_id == notebook.id)
            )
            if existing is None:
                raise
            return existing

        await self._db.refresh(session)
        return session

    async def list_messages(self, session_id: UUID) -> list[ChatMessage]:
        result = await self._db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        )
        return list(result.scalars().all())

    async def create_message(
        self,
        *,
        session_id: UUID,
        role: ChatMessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
        touch_session: bool = False,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=metadata or {},
        )
        if touch_session:
            session = await self._db.get(ChatSession, session_id)
            if session is not None:
                session.updated_at = datetime.now(timezone.utc)
        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)
        return message
