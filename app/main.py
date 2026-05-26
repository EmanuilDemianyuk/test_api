import asyncio

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from app.api.v1.category import router as category_router
from app.api.v1.product import router as product_router
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.seeders import ensure_demo_data


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