from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, notebooks, upload, users
from app.core.config import settings
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await async_engine.dispose()


app = FastAPI(title="Paper Craft", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router, prefix="/api/v1")
app.include_router(notebooks.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
