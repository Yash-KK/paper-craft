# chat/service.py
import asyncio
from collections.abc import AsyncIterator, Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.db.models.chat import ChatMessage, ChatMessageRole, ChatSession
from app.db.models.notebook import Notebook
from app.db.models.user import User
from app.repositories.chat import ChatRepository
from app.schemas.chat import ChatSessionResponse
from app.services.chat.agent import stream_notebook_chat


class ChatService:
    """Orchestrates notebook chat sessions and streaming turns."""

    def __init__(self, repository: ChatRepository) -> None:
        self._repo = repository

    async def _require_owned_notebook(self, notebook_id: UUID, user: User) -> Notebook:
        notebook = await self._repo.get_owned_notebook(notebook_id, user)
        if notebook is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found"
            )
        return notebook

    async def get_or_create_owned_session(
        self, notebook_id: UUID, user: User
    ) -> ChatSession:
        notebook = await self._require_owned_notebook(notebook_id, user)
        return await self._repo.get_or_create_session(notebook)

    async def get_chat(self, notebook_id: UUID, user: User) -> ChatSessionResponse:
        session = await self.get_or_create_owned_session(notebook_id, user)
        return ChatSessionResponse.model_validate(session)

    def messages_cursor_query(self, session_id: UUID):
        return self._repo.messages_cursor_query(session_id)

    async def start_turn(
        self,
        *,
        notebook_id: UUID,
        user: User,
        content: str,
        top_k: int,
        enabled_tools: Sequence[str] | None = None,
    ) -> AsyncIterator[dict[str, str]]:
        """Validate ownership, persist the user message, then return the SSE generator."""
        notebook = await self._require_owned_notebook(notebook_id, user)
        session = await self._repo.get_or_create_session(notebook)
        history = await self._repo.list_recent_messages(session.id, limit=20)
        await self._repo.create_message(
            session_id=session.id, role=ChatMessageRole.USER, content=content
        )

        return self._generate_turn(
            question=content,
            history=history,
            selected_chapters=list(notebook.selected_chapters),
            board=notebook.board.value if notebook.board else None,
            top_k=top_k,
            enabled_tools=frozenset(enabled_tools or ()),
            session_id=session.id,
        )

    async def _generate_turn(
        self,
        *,
        question: str,
        history: list[ChatMessage],
        selected_chapters: list,
        board: str | None,
        top_k: int,
        enabled_tools: frozenset[str],
        session_id: UUID,
    ) -> AsyncIterator[dict[str, str]]:
        try:
            async for event in stream_notebook_chat(
                question=question,
                history=history,
                selected_chapters=selected_chapters,
                board=board,
                top_k=top_k,
                enabled_tools=enabled_tools,
            ):
                if event["event"] == "done":
                    answer = event["data"]
                    if answer:
                        await self._repo.create_message(
                            session_id=session_id,
                            role=ChatMessageRole.ASSISTANT,
                            content=answer,
                            touch_session=True,
                        )
                    yield {"event": "done", "data": ""}
                    return
                yield event
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — SSE boundary: any turn failure → error event
            yield {"event": "error", "data": str(exc)}
