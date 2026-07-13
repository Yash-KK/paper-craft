from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from sqlalchemy import select

from app.api.deps import SessionDep, get_google_sso
from app.core.config import settings
from app.core.security import create_access_token
from app.db.models.user import User, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(sso: GoogleSSO = Depends(get_google_sso)):
    """Redirect the user to Google for SSO."""
    async with sso:
        return await sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )


@router.get("/callback")
async def callback(
    request: Request,
    db: SessionDep,
    sso: GoogleSSO = Depends(get_google_sso),
):
    """Handle the Google redirect, upsert the user, and hand a JWT to the frontend."""
    try:
        async with sso:
            google_user = await sso.verify_and_process(request)
    except Exception:
        return RedirectResponse(f"{settings.frontend_url}?auth_error=true")

    if google_user is None or not google_user.id:
        return RedirectResponse(f"{settings.frontend_url}?auth_error=true")

    result = await db.execute(
        select(User).where(User.auth_provider_id == google_user.id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=google_user.email,
            auth_provider="google",
            auth_provider_id=google_user.id,
            full_name=google_user.display_name or google_user.email,
            email_verified=True,
            profile=UserProfile(avatar_url=google_user.picture),
        )
        db.add(user)
    else:
        if user.profile is None:
            user.profile = UserProfile(avatar_url=google_user.picture)
        elif google_user.picture:
            user.profile.avatar_url = google_user.picture

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(subject=str(user.id))
    return RedirectResponse(f"{settings.frontend_url}?token={access_token}")
