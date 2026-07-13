from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import auth, upload, users
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await async_engine.dispose()


app = FastAPI(title="Paper Craft", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
