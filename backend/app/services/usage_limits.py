"""Per-account usage quotas (lifetime counters; deletes do not restore)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UsageLimitExceededError(RuntimeError):
    """Raised when an account has exhausted a generation or chat quota."""


async def consume_question_paper_quota(db: AsyncSession, user: User) -> None:
    await db.refresh(user, with_for_update=True)
    if user.question_paper_usage >= user.question_paper_limit:
        raise UsageLimitExceededError(
            "Question paper limit reached "
            f"({user.question_paper_usage}/{user.question_paper_limit})"
        )
    user.question_paper_usage += 1


async def consume_chat_message_quota(db: AsyncSession, user: User) -> None:
    await db.refresh(user, with_for_update=True)
    if user.chat_message_usage >= user.chat_message_limit:
        raise UsageLimitExceededError(
            "Chat message limit reached "
            f"({user.chat_message_usage}/{user.chat_message_limit})"
        )
    user.chat_message_usage += 1
