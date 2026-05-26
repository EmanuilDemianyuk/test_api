import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import db as db_module
from app.core.config import settings
from app.main import app as fastapi_app
from tests.seeders import cleanup_seed_data, seed_test_data


def install_test_db() -> None:
    engine = create_async_engine(
        settings.database_url,
        future=True,
    )
    sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    db_module.engine = engine
    db_module.AsyncSessionLocal = sessionmaker
    fastapi_app.AsyncSessionLocal = sessionmaker


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_engine():
    install_test_db()

    try:
        yield db_module.engine
    finally:
        await db_module.engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with db_module.AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await cleanup_seed_data(session)


@pytest_asyncio.fixture
async def seeded_test_data(db_session: AsyncSession):
    return await seed_test_data(db_session)


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    original_overrides = fastapi_app.dependency_overrides.copy()
    fastapi_app.dependency_overrides[db_module.get_db] = override_get_db

    transport = ASGITransport(app=fastapi_app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        fastapi_app.dependency_overrides.clear()
        fastapi_app.dependency_overrides.update(original_overrides)
