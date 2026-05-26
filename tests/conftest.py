from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal, engine
from tests.seeders import cleanup_seed_data, seed_test_data


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await cleanup_seed_data(session)

    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_test_data(db_session: AsyncSession):
    return await seed_test_data(db_session)
