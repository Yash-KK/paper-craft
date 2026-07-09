from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1 import upload
from app.core.config import PROJECT_ROOT


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dotenv(PROJECT_ROOT / ".env")
    yield


app = FastAPI(title="Paper Craft", lifespan=lifespan)

app.include_router(upload.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
