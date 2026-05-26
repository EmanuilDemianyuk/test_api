from decimal import Decimal

import pytest
import pytest_asyncio

from app.core.db import AsyncSessionLocal, engine
from app.core.enums import StatusEnum
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreateSchema, ProductUpdateSchema
from app.services.product import ProductService


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine_between_tests():
    yield
    await engine.dispose()


async def create_product_via_service(name: str, seo_keyword: str) -> int:
    async with AsyncSessionLocal() as session:
        repository = ProductRepository(session)
        service = ProductService(repository, session)

        created = await service.create_product(
            ProductCreateSchema(
                name=name,
                description="Created for transaction verification",
                seo_keyword=seo_keyword,
                status=StatusEnum.ENABLED,
                price=Decimal("12.50"),
                model="TXN-001",
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
async def test_post_product_persists_to_database():
    product_id = await create_product_via_service(
        "Post persistence test",
        "post-persistence-test",
    )

    try:
        async with AsyncSessionLocal() as session:
            product = await session.get(Product, product_id)

        assert product is not None
        assert product.name == "Post persistence test"
    finally:
        await cleanup_product(product_id)


@pytest.mark.asyncio
async def test_update_product_persists_to_database():
    product_id = await create_product_via_service(
        "Update persistence test",
        "update-persistence-test",
    )

    try:
        async with AsyncSessionLocal() as session:
            repository = ProductRepository(session)
            product = await repository.get_by_id(product_id)
            assert product is not None

            service = ProductService(repository, session)
            await service.update_product(
                product,
                ProductUpdateSchema(
                    name="Updated persistence test",
                    description="Updated description",
                    price=Decimal("19.99"),
                    status=StatusEnum.ENABLED,
                ),
            )

        async with AsyncSessionLocal() as session:
            persisted = await session.get(Product, product_id)

        assert persisted is not None
        assert persisted.name == "Updated persistence test"
        assert persisted.description == "Updated description"
        assert persisted.price == Decimal("19.99")
    finally:
        await cleanup_product(product_id)


@pytest.mark.asyncio
async def test_delete_product_removes_record_from_database():
    product_id = await create_product_via_service(
        "Delete persistence test",
        "delete-persistence-test",
    )

    try:
        async with AsyncSessionLocal() as session:
            repository = ProductRepository(session)
            product = await repository.get_by_id(product_id)
            assert product is not None

            service = ProductService(repository, session)
            await service.delete_product(product)

        async with AsyncSessionLocal() as session:
            persisted = await session.get(Product, product_id)

        assert persisted is None
    finally:
        await cleanup_product(product_id)
