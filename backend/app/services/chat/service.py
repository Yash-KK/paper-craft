# chat/service.py
import asyncio
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status

from app.db.models.chat import ChatMessage, ChatMessageRole
from app.db.models.user import User
from app.repositories.chat import ChatRepository
from app.schemas.chat import ChatMessageResponse, ChatSessionDetail
from app.services.chat.agent import stream_notebook_chat
from app.services.chat.streaming import sse_event


class ChatService:
    """Orchestrates notebook chat sessions and streaming turns."""

    def __init__(self, repository: ChatRepository) -> None:
        self._repo = repository

    async def get_chat(self, notebook_id: UUID, user: User) -> ChatSessionDetail:
        notebook = await self._repo.get_owned_notebook(notebook_id, user)
        if notebook is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

        session = await self._repo.get_or_create_session(notebook)
        messages = await self._repo.list_messages(session.id)

        return ChatSessionDetail(
            id=session.id,
            notebook_id=session.notebook_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=[ChatMessageResponse.model_validate(message) for message in messages],
        )

    async def start_turn(
        self,
        *,
        notebook_id: UUID,
        user: User,
        content: str,
        top_k: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """Validate ownership, persist the user message, then return the SSE generator.

        Ownership and persistence run before the generator is returned so HTTP
        errors still surface as normal status codes (not mid-stream events).
        """
        notebook = await self._repo.get_owned_notebook(notebook_id, user)
        if notebook is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

        session = await self._repo.get_or_create_session(notebook)
        history = await self._repo.list_messages(session.id)

        user_message = await self._repo.create_message(
            session_id=session.id,
            role=ChatMessageRole.USER,
            content=content,
        )
        user_payload = ChatMessageResponse.model_validate(user_message).model_dump(mode="json")

        return self._generate_turn(
            question=content,
            history=history,
            selected_chapters=list(notebook.selected_chapters),
            top_k=top_k,
            session_id=session.id,
            user_payload=user_payload,
        )

    async def _generate_turn(
        self,
        *,
        question: str,
        history: list[ChatMessage],
        selected_chapters: list[dict[str, Any]],
        top_k: int,
        session_id: UUID,
        user_payload: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        try:
            async for event in stream_notebook_chat(
                question=question,
                history=history,
                selected_chapters=selected_chapters,
                top_k=top_k,
            ):
                event_type = event.get("type")

                if event_type == "complete":
                    async for item in self._persist_assistant_and_done(
                        session_id=session_id, user_payload=user_payload, event=event
                    ):
                        yield item
                    return

                if event_type == "error":
                    yield sse_event(
                        {
                            "type": "error",
                            "message": event.get("message")
                            or "The chat service could not generate a response",
                        }
                    )
                    return

                yield sse_event(event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield sse_event({"type": "error", "message": str(exc)})

    async def _persist_assistant_and_done(
        self,
        *,
        session_id: UUID,
        user_payload: dict[str, Any],
        event: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        answer = event.get("answer") or ""
        if not answer:
            yield sse_event(
                {"type": "error", "message": "The chat service could not generate a response"}
            )
            return

        assistant_message = await self._repo.create_message(
            session_id=session_id,
            role=ChatMessageRole.ASSISTANT,
            content=answer,
            metadata={"tool_calls": event.get("tool_calls") or []},
            touch_session=True,
        )

        yield sse_event(
            {
                "type": "done",
                "session_id": str(session_id),
                "user_message": user_payload,
                "assistant_message": ChatMessageResponse.model_validate(
                    assistant_message
                ).model_dump(mode="json"),
            }
        )