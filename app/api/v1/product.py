from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from app.core.pagination import PaginatedResponse
from app.repositories.product import ProductRepository

from app.services.product import ProductService

from app.schemas.product import (
    ProductCategoryCreateSchema,
    ProductCategoryResponseSchema,
    ProductCreateSchema,
    ProductDetailSchema,
    ProductListItemSchema,
    ProductUpdateSchema,
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
    status_code=status.HTTP_201_CREATED,
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


@router.patch(
    "/{product_id}",
    response_model=ProductDetailSchema,
)
async def update_product(
    product_id: int,
    payload: ProductUpdateSchema,
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

    return await service.update_product(
        product,
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


@router.delete(
    "/{product_id}",
    status_code=204,
)
async def delete_product(
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

    await service.delete_product(product)

    return Response(status_code=204)


@router.get(
    "/{product_id}/category",
    response_model=list[
        ProductCategoryResponseSchema,
    ],
)
async def get_product_categories(
    product_id: int,
    service: ProductService = Depends(
        get_product_service,
    ),
):
    return await service.get_product_categories(
        product_id,
    )


@router.post(
    "/{product_id}/category",
    response_model=ProductCategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_category(
    product_id: int,
    payload: ProductCategoryCreateSchema,
    service: ProductService = Depends(
        get_product_service,
    ),
):
    return await service.create_product_category(
        product_id,
        payload.category_id,
    )


@router.delete(
    "/{product_id}/category/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product_category(
    product_id: int,
    category_id: int,
    service: ProductService = Depends(
        get_product_service,
    ),
):
    await service.delete_product_category(
        product_id,
        category_id,
    )

    return Response(status_code=204)



