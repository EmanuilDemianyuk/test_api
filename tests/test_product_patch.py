from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.db import AsyncSessionLocal, engine
from app.core.enums import StatusEnum
from app.main import app
from app.models.category import Category
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreateSchema
from app.services.product import ProductService


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine_between_tests():
    yield
    await engine.dispose()


async def create_category(name: str) -> int:
    async with AsyncSessionLocal() as session:
        category = Category(name=name, status=StatusEnum.ENABLED)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category.category_id


async def create_product(name: str, seo_keyword: str) -> int:
    async with AsyncSessionLocal() as session:
        repository = ProductRepository(session)
        service = ProductService(repository, session)

        created = await service.create_product(
            ProductCreateSchema(
                name=name,
                description="Original description",
                seo_keyword=seo_keyword,
                status=StatusEnum.DISABLED,
                price=Decimal("10.00"),
                model="PATCH-1",
                manufacturer_id=1,
                categories=[],
                images=[],
                attributes=[],
            )
        )

        return created.product_id


async def cleanup_product(product_id: int) -> None:
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product is not None:
            await session.delete(product)
            await session.commit()


async def cleanup_category(category_id: int) -> None:
    async with AsyncSessionLocal() as session:
        category = await session.get(Category, category_id)
        if category is not None:
            await session.delete(category)
            await session.commit()


@pytest.mark.asyncio
async def test_patch_product_partial_update_persists_changes():
    product_id = await create_product("Original product", "patch-product-partial")
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                f"/product/{product_id}",
                json={"name": "Patched product"},
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["product_id"] == product_id
        assert payload["name"] == "Patched product"
        assert payload["description"] == "Original description"

        async with AsyncSessionLocal() as session:
            persisted = await session.get(Product, product_id)

        assert persisted is not None
        assert persisted.name == "Patched product"
        assert persisted.description == "Original description"
    finally:
        await cleanup_product(product_id)


@pytest.mark.asyncio
async def test_patch_product_returns_422_for_invalid_payload():
    product_id = await create_product("Invalid payload product", "patch-product-invalid-payload")
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                f"/product/{product_id}",
                json={"status": "not-a-valid-status"},
            )

        assert response.status_code == 422
    finally:
        await cleanup_product(product_id)


@pytest.mark.asyncio
async def test_patch_product_returns_404_for_invalid_category():
    product_id = await create_product("Category validation product", "patch-product-invalid-category")
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                f"/product/{product_id}",
                json={"categories": [{"category_id": 999999}]},
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"
    finally:
        await cleanup_product(product_id)
