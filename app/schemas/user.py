from pydantic import BaseModel


class UserProfile(BaseModel):
    """Authenticated user returned by the SSO provider."""

    id: str | None = None
    email: str | None = None
    display_name: str | None = None
    picture: str | None = None
    provider: str | None = None

