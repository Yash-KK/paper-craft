from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.user import UserRole


class UserProfileUpdate(BaseModel):
    school_name: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    user_id: UUID
    email: str
    full_name: str
    role: UserRole
    school_name: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    settings: dict = Field(default_factory=dict)
