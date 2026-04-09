from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes.student import router as student_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="ynov-cicd-tp03", lifespan=lifespan)
app.include_router(student_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
