import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.db import AsyncSessionLocal, engine
from app.core.enums import StatusEnum
from app.main import app
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreateSchema
from app.services.product import ProductService


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine_between_tests():
    yield
    await engine.dispose()


async def create_product(name: str, seo_keyword: str) -> int:
    async with AsyncSessionLocal() as session:
        repository = ProductRepository(session)
        service = ProductService(repository, session)

        created = await service.create_product(
            ProductCreateSchema(
                name=name,
                description="Delete test product",
                seo_keyword=seo_keyword,
                status=StatusEnum.DISABLED,
                price=None,
                model="DEL-1",
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


@pytest.mark.asyncio
async def test_delete_product_removes_record():
    product_id = await create_product("Delete me", "delete-product-success")

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.delete(f"/product/{product_id}")

        assert response.status_code == 204

        async with AsyncSessionLocal() as session:
            deleted = await session.get(Product, product_id)

        assert deleted is None
    finally:
        await cleanup_product(product_id)


@pytest.mark.asyncio
async def test_delete_product_returns_404_for_missing_product():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.delete("/product/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
