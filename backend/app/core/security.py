from datetime import datetime, timedelta, timezone
from functools import lru_cache

from fastapi_sso.sso.google import GoogleSSO
from jose import jwt

from app.core.config import settings


@lru_cache
def get_google_sso() -> GoogleSSO:
    """Cached Google SSO client built from application settings."""
    return GoogleSSO(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=settings.google_redirect_uri,
        allow_insecure_http=settings.allow_insecure_http,
    )


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Sign a JWT for an authenticated user (subject is the user id)."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, raising jose.JWTError on failure."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
