from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.application.exceptions import NotFoundError
from app.domain.exceptions import DomainError
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.postgres.db import get_engine
from app.infrastructure.http.departments import router
from app.infrastructure.storage.s3.storage import try_ensure_bucket


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    get_settings()
    get_engine()
    try_ensure_bucket()
    yield


app = FastAPI(
    title="Lebane API",
    description="API del panel de departamentos. Contrato HTTP en español (enunciado).",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in get_settings().cors_origins.split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


@app.exception_handler(NotFoundError)
async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
