from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import StatusEnum
from app.models.category import Category
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.product_category import ProductCategory
from app.models.product_image import ProductImage
from app.models.store import Store
from app.repositories.category import CategoryRepository


@dataclass
class SeededCategoryTree:
    root_category: Category
    child_category: Category


@dataclass
class SeededProduct:
    product: Product
    product_category: ProductCategory
    product_image: ProductImage
    product_attribute: ProductAttribute


@dataclass
class SeededTestData:
    category_tree: SeededCategoryTree
    product: SeededProduct


async def seed_test_data(
    session: AsyncSession,
    suffix: str | None = None,
) -> SeededTestData:
    seed_suffix = suffix or uuid4().hex[:8]
    repository = CategoryRepository(session)

    root_category = await repository.create(
        {
            "name": f"Root-{seed_suffix}",
            "status": StatusEnum.ENABLED,
        }
    )

    child_category = await repository.create(
        {
            "name": f"Child-{seed_suffix}",
            "parent_category_id": root_category.category_id,
            "status": StatusEnum.ENABLED,
        }
    )

    product = Product(
        name=f"Seed Product-{seed_suffix}",
        description="Seeded product for tests",
        seo_keyword=f"seed-product-{seed_suffix}",
        meta_title=f"Seed Product-{seed_suffix}",
        meta_description="Seeded product metadata",
        meta_keyword="seed, test",
        image="https://example.com/images/seed-product.png",
        status=StatusEnum.ENABLED,
        price=199.99,
        model=f"SEED-{seed_suffix}",
        manufacturer_id=1,
    )

    session.add(product)
    await session.flush()

    product_category = ProductCategory(
        product_id=product.product_id,
        category_id=child_category.category_id,
    )

    product_image = ProductImage(
        product_id=product.product_id,
        image="https://example.com/images/seed-product-1.png",
        sort_order=0,
    )

    product_attribute = ProductAttribute(
        product_id=product.product_id,
        group_name="Details",
        name="Size",
        value="M",
        sort_order=0,
    )

    session.add_all([product_category, product_image, product_attribute])
    await session.commit()
    await session.refresh(product)

    return SeededTestData(
        category_tree=SeededCategoryTree(
            root_category=root_category,
            child_category=child_category,
        ),
        product=SeededProduct(
            product=product,
            product_category=product_category,
            product_image=product_image,
            product_attribute=product_attribute,
        ),
    )


async def create_product(
    session: AsyncSession,
    name: str,
    seo_keyword: str,
) -> int:
    seeded = await seed_test_data(session)

    product = seeded.product.product

    product.name = name
    product.seo_keyword = seo_keyword

    await session.commit()
    await session.refresh(product)

    return product.product_id


async def create_store(
    session: AsyncSession,
    name: str,
) -> int:
    store = Store(
        name=name,
    )

    session.add(store)

    await session.commit()
    await session.refresh(store)

    return store.store_id    



async def cleanup_seed_data(session: AsyncSession) -> None:
    await session.execute(sa.delete(ProductAttribute))
    await session.execute(sa.delete(ProductImage))
    await session.execute(sa.delete(ProductCategory))
    await session.execute(sa.delete(Product))
    await session.execute(sa.delete(Store))
    await session.execute(sa.delete(Category))
    await session.commit()
