from fastapi import APIRouter, Depends, Request
from fastapi_sso.sso.google import GoogleSSO

from app.api.deps import get_google_sso
from app.schemas.user import UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(sso: GoogleSSO = Depends(get_google_sso)):
    """Initialize auth and redirect to Google."""
    async with sso:
        return await sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )


@router.get("/callback", response_model=UserProfile)
async def callback(
    request: Request, sso: GoogleSSO = Depends(get_google_sso)
) -> UserProfile:
    """Verify the SSO callback and return the authenticated user."""
    async with sso:
        user = await sso.verify_and_process(request)
    return UserProfile(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        picture=user.picture,
        provider=user.provider,
    )
