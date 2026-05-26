import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.db import AsyncSessionLocal, engine
from app.core.enums import StatusEnum
from app.main import app
from app.models.category import Category


async def create_category(name: str) -> int:
    async with AsyncSessionLocal() as session:
        category = Category(name=name, status=StatusEnum.ENABLED)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category.category_id


async def cleanup_category(category_id: int) -> None:
    async with AsyncSessionLocal() as session:
        category = await session.get(Category, category_id)
        if category is not None:
            await session.delete(category)
            await session.commit()


@pytest.mark.asyncio
async def test_patch_category_persists_changes():
    await engine.dispose()
    category_id = await create_category("Original category")

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                f"/category/{category_id}",
                json={
                    "name": "Updated category",
                    "description": "Persisted description",
                    "status": 1,
                },
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["name"] == "Updated category"
        assert payload["description"] == "Persisted description"

        async with AsyncSessionLocal() as session:
            refreshed = await session.scalar(
                select(Category).where(Category.category_id == category_id)
            )

        assert refreshed is not None
        assert refreshed.name == "Updated category"
        assert refreshed.description == "Persisted description"
    finally:
        await cleanup_category(category_id)
        await engine.dispose()


@pytest.mark.asyncio
async def test_delete_category_removes_record():
    await engine.dispose()
    category_id = await create_category("Delete me")

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.delete(f"/category/{category_id}")

        assert response.status_code == 204

        async with AsyncSessionLocal() as session:
            deleted = await session.scalar(
                select(Category).where(Category.category_id == category_id)
            )

        assert deleted is None
    finally:
        await cleanup_category(category_id)
        await engine.dispose()
