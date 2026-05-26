from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from app.repositories.category import (
    CategoryRepository,
)

from app.schemas.category import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryResponseSchema,
)

from app.services.category import (
    CategoryService,
)


router = APIRouter(
    prefix="/category",
    tags=["Category"],
)


async def get_category_service(
    session: AsyncSession = Depends(get_db),
):
    repository = CategoryRepository(session)

    return CategoryService(
        repository,
        session,
    )

@router.get("")
async def get_categories(
    page: int = 1,
    size: int = 20,
    search: str | None = None,
    status: int | None = None,
    sort_by: str = "full_path",
    sort_order: str = "asc",
    service: CategoryService = Depends(
        get_category_service
    ),
):
    items, total = await service.get_categories(
        page=page,
        size=size,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }

@router.get(
    "/{category_id}",
    response_model=CategoryResponseSchema,
)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(
        get_category_service
    ),
):
    category = await service.get_category(
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category

@router.post(
    "",
    response_model=CategoryResponseSchema,
    status_code=201,
)
async def create_category(
    payload: CategoryCreateSchema,
    service: CategoryService = Depends(
        get_category_service,
    ),
):
    return await service.create_category(
        payload,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponseSchema,
)
async def update_category(
    category_id: int,
    payload: CategoryUpdateSchema,
    service: CategoryService = Depends(
        get_category_service,
    ),
):
    category = await service.get_category(
        category_id,
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return await service.update_category(
        category,
        payload,
    )


@router.delete(
    "/{category_id}",
    status_code=204,
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(
        get_category_service,
    ),
):
    category = await service.get_category(
        category_id,
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",        )

    await service.delete_category(category)    