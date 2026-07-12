from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1 import upload
from app.core.config import PROJECT_ROOT

import os
from fastapi import Request
from fastapi_sso.sso.google import GoogleSSO

load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dotenv(PROJECT_ROOT / ".env")
    yield

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/callback",
    allow_insecure_http=True,
)

app = FastAPI(title="Paper Craft", lifespan=lifespan)






@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
    return user
app.include_router(upload.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
