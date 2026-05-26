import asyncio
import logging

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.v1.category import router as category_router
from app.api.v1.product import router as product_router
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.seeders import ensure_demo_data

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        settings.database_url.replace(
            "mysql+aiomysql://",
            "mysql+pymysql://",
        ),
    )
    command.upgrade(config, "head")


app = FastAPI(
    title="Shop API",
    version="1.0.0",
)


def error_response(status_code: int, detail):
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return error_response(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return error_response(422, exc.errors())


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(_: Request, exc: IntegrityError):
    return error_response(409, "Database integrity error")


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return error_response(400, "Bad request")


@app.on_event("startup")
async def startup() -> None:
    await asyncio.to_thread(run_migrations)

    if settings.AUTO_SEED_TEST_DATA:
        async with AsyncSessionLocal() as session:
            await ensure_demo_data(session)


@app.get("/")
async def root():
    return {
        "status": "ok",
    }


app.include_router(category_router)
app.include_router(product_router)