from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Optional API-key guard. Skipped when API_KEY is empty."""
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
