from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

from app.repositories.category import (
    CategoryRepository,
)

from app.schemas.category import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
)


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.session = session

    async def create_category(
        self,
        payload: CategoryCreateSchema,
    ):
        try:
            if payload.parent_category_id:
                parent = await self.repository.get_by_id(
                    payload.parent_category_id,
                )
    
                if not parent:
                    raise HTTPException(
                        status_code=404,
                        detail="Parent category not found",
                    )
    
            category = await self.repository.create(
                payload.model_dump(),
            )
    
            await self.session.commit()
    
            await self.session.refresh(category)

            return category

        except IntegrityError as exc:
            await self.session.rollback()
            message = str(exc.orig).lower()
            if "duplicate" in message or "unique" in message:
                raise HTTPException(
                    status_code=409,
                    detail="Category with this SEO keyword already exists",
                )
            raise

        except Exception:
            await self.session.rollback()
            raise

    async def get_categories(
        self,
        page: int,
        size: int,
        search: str | None,
        status: int | None,
        sort_by: str,
        sort_order: str,
    ):
        return await self.repository.get_categories(
            page=page,
            size=size,
            search=search,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_category(
        self,
        category_id: int,
    ):
        return await self.repository.get_by_id(
            category_id
        )

    async def update_category(
        self,
        category: Category,
        payload: CategoryUpdateSchema,
    ):
        update_data = payload.model_dump(
            exclude_unset=True,
        )

        parent_category_id = update_data.get(
            "parent_category_id",
        )

        if parent_category_id == category.category_id:
            raise HTTPException(
                status_code=400,
                detail="A category cannot be its own parent",
            )

        for key, value in update_data.items():
            setattr(category, key, value)

        await self.session.flush()
        self.repository.set_full_path(category)

        return category
    
    async def delete_category(
        self,
        category,
    ):
        await self.repository.delete(category)