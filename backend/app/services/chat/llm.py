from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.core.config import settings


@lru_cache
def get_chat_model() -> ChatOpenAI:
    """Return the shared chat model used by notebook agents."""
    return ChatOpenAI(
        model=settings.aic_model,
        api_key=settings.aic_api_key,
        base_url=settings.aic_base_url,
    )
