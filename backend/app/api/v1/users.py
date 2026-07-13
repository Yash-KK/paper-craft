from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.db.models.user import User, UserProfile
from app.schemas.user import UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _to_response(user: User) -> UserProfileResponse:
    profile = user.profile
    return UserProfileResponse(
        id=profile.id if profile else None,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        school_name=profile.school_name if profile else None,
        phone_number=profile.phone_number if profile else None,
        avatar_url=profile.avatar_url if profile else None,
        settings=profile.settings if profile else {},
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: CurrentUser) -> UserProfileResponse:
    return _to_response(current_user)


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    updates: UserProfileUpdate,
    current_user: CurrentUser,
    db: SessionDep,
) -> UserProfileResponse:
    profile = current_user.profile
    if profile is None:
        profile = UserProfile(user_id=current_user.id)
        current_user.profile = profile
        db.add(profile)

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(current_user)
    return _to_response(current_user)
