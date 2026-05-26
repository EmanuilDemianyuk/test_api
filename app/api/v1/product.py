from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from app.core.pagination import PaginatedResponse
from app.repositories.product import ProductRepository

from app.services.product import ProductService

from app.schemas.product import (
    ProductCreateSchema,
    ProductDetailSchema,
    ProductListItemSchema,
)


router = APIRouter(
    prefix="/product",
    tags=["Product"],
)


async def get_product_service(
    session: AsyncSession = Depends(get_db),
):
    repository = ProductRepository(session)

    return ProductService(
        repository,
        session,
    )

@router.get(
    "",
    response_model=PaginatedResponse[ProductListItemSchema],
)
async def get_products(
    page: int = 1,
    size: int = 20,
    service: ProductService = Depends(
        get_product_service,
    ),
):
    items, total = await service.get_products(
        page=page,
        size=size,
    )

    return {
        "items": [
            ProductListItemSchema(**item)
            for item in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }

@router.post(
    "",
    response_model=ProductDetailSchema,
)
async def create_product(
    payload: ProductCreateSchema,
    service: ProductService = Depends(
        get_product_service,
    ),
):
    return await service.create_product(
        payload,
    )

@router.get(
    "/{product_id}",
    response_model=ProductDetailSchema,
)
async def get_product(
    product_id: int,
    service: ProductService = Depends(
        get_product_service,
    ),
): 
    product = await service.repository.get_by_id(
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product