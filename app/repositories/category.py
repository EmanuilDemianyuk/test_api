from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import StatusEnum
from app.models.category import Category
from app.utils.category_tree import build_category_full_paths
from app.utils.category_tree import build_full_path


class CategoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    def set_full_path(
        self,
        category: Category,
    ) -> None:
        category.full_path = build_full_path(
            category,
            {category.category_id: category},
        )

    async def create(
        self,
        payload,
    ) -> Category:
        category = Category(**payload)

        self.session.add(category)

        await self.session.flush()
        await self.session.refresh(category)
        self.set_full_path(category)

        return category

    async def get_by_id(
        self,
        category_id: int,
    ) -> Category | None:
        stmt = (
            select(Category)
            .where(Category.category_id == category_id)
        )

        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()

        if category is not None:
            self.set_full_path(category)

        return category

    async def delete(
        self,
        category: Category,
    ) -> None:
        await self.session.delete(category)

    async def get_categories(
        self,
        page: int,
        size: int,
        search: str | None = None,
        status: int | None = None,
        sort_by: str = "full_path",
        sort_order: str = "asc",
    ):
        stmt = select(Category)

        if status is not None:
            stmt = stmt.where(
                Category.status == StatusEnum(status)
            )

        result = await self.session.execute(stmt)
        categories = result.scalars().all()

        full_paths = build_category_full_paths(categories)

        for category in categories:
            category.full_path = full_paths[
                category.category_id
            ]

        if search:
            categories = [
                category
                for category in categories
                if search.lower() in category.full_path.lower()
            ]

        sort_key = (
            lambda category: category.full_path
            if sort_by == "full_path"
            else category.category_id
        )

        categories = sorted(
            categories,
            key=sort_key,
            reverse=sort_order == "desc",
        )

        total = len(categories)
        start = (page - 1) * size
        end = start + size

        return categories[start:end], total