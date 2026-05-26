import asyncio
from uuid import uuid4

import pytest

from app.api.v1.category import get_categories
from app.core.db import AsyncSessionLocal
from app.core.enums import StatusEnum
from app.main import app
from app.models.category import Category
from app.models.product_category import ProductCategory
from app.repositories.category import CategoryRepository
from app.utils.category_tree import build_category_full_paths


async def create_category_path_tree():
    suffix = uuid4().hex[:8]

    async with AsyncSessionLocal() as session:
        root = Category(
            name=f"A-{suffix}",
            status=StatusEnum.ENABLED,
        )
        session.add(root)
        await session.flush()

        child = Category(
            name=f"B-{suffix}",
            parent=root,
            status=StatusEnum.ENABLED,
        )
        leaf = Category(
            name=f"C-{suffix}",
            parent=child,
            status=StatusEnum.ENABLED,
        )

        session.add_all([child, leaf])
        await session.commit()

        return root, child, leaf


async def cleanup_category_path_tree(root: Category):
    async with AsyncSessionLocal() as session:
        category = await session.get(Category, root.category_id)

        if category is not None:
            await session.delete(category)
            await session.commit()


@pytest.mark.asyncio
async def test_category_repository_search_uses_full_path():
    root, child, leaf = await create_category_path_tree()
    try:
        async with AsyncSessionLocal() as session:
            repository = CategoryRepository(session)
            items, total = await repository.get_categories(
                page=1,
                size=20,
                search=f"{root.name} > {child.name} > {leaf.name}",
            )

        assert total >= 1
        assert any(
            item.full_path == f"{root.name} > {child.name} > {leaf.name}"
            for item in items
        )
    finally:
        await cleanup_category_path_tree(root)


@pytest.mark.asyncio
async def test_category_endpoint_search_uses_full_path():
    class StubCategoryService:
        def __init__(self):
            self.last_search = None

        async def get_categories(self, page, size, search, status, sort_by, sort_order):
            self.last_search = search
            category = Category(name="A")
            category.full_path = "A > B > C"
            return [category], 1

    service = StubCategoryService()

    response = await get_categories(
        page=1,
        size=20,
        search="A > B > C",
        status=None,
        sort_by="full_path",
        sort_order="asc",
        service=service,
    )

    assert service.last_search == "A > B > C"
    assert response["total"] == 1
    assert response["items"][0].name == "A"
    assert response["items"][0].full_path == "A > B > C"


def test_build_category_full_paths():
    root = Category(name="A")
    child = Category(name="B", parent=root)
    leaf = Category(name="C", parent=child)

    root.category_id = 1
    child.category_id = 2
    leaf.category_id = 3

    full_paths = build_category_full_paths([root, child, leaf])

    assert full_paths == {
        1: "A",
        2: "A > B",
        3: "A > B > C",
    }


def test_product_category_full_path_and_name():
    root = Category(name="A")
    child = Category(name="B", parent=root)
    leaf = Category(name="C", parent=child)

    product_category = ProductCategory(category=leaf)

    assert product_category.category_name == "C"
    assert product_category.full_path == "A > B > C"


def test_product_router_is_registered():
    assert any(
        route.path == "/product/{product_id}"
        for route in app.routes
    )
