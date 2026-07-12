from functools import lru_cache

from fastapi_sso.sso.google import GoogleSSO

from app.core.config import settings


@lru_cache
def get_google_sso() -> GoogleSSO:
    return GoogleSSO(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=settings.google_redirect_uri,
        allow_insecure_http=settings.allow_insecure_http,
    )
