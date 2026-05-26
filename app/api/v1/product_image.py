from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from app.repositories.product_image import (
    ProductImageRepository,
)

from app.repositories.product import (
    ProductRepository,
)

from app.services.product_image import (
    ProductImageService,
)

from app.schemas.product_image import (
    ProductImageCreateSchema,
    ProductImageResponseSchema,
)


router = APIRouter(
    prefix="/product",
    tags=["Product Images"],
)

async def get_product_image_service(
    session: AsyncSession = Depends(get_db),
):
    repository = ProductImageRepository(
        session,
    )

    return ProductImageService(
        repository,
        session,
    )


async def validate_product_exists(
    product_id: int,
    session: AsyncSession,
):
    repository = ProductRepository(session)

    product = await repository.get_by_id(
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    
@router.get(
    "/{product_id}/image",
    response_model=list[
        ProductImageResponseSchema
    ],
)
async def get_product_images(
    product_id: int,
    service: ProductImageService = Depends(
        get_product_image_service,
    ),
    session: AsyncSession = Depends(get_db),
):
    await validate_product_exists(
        product_id,
        session,
    )

    return await service.get_product_images(
        product_id,
    )

@router.post(
    "/{product_id}/image",
    response_model=ProductImageResponseSchema,
    status_code=201,
)
async def create_product_image(
    product_id: int,
    payload: ProductImageCreateSchema,
    service: ProductImageService = Depends(
        get_product_image_service,
    ),
    session: AsyncSession = Depends(get_db),
):
    await validate_product_exists(
        product_id,
        session,
    )

    return await service.create_image(
        product_id,
        payload,
    )

@router.delete(
    "/{product_id}/image/{image_id}",
    status_code=204,
)
async def delete_product_image(
    product_id: int,
    image_id: int,
    service: ProductImageService = Depends(
        get_product_image_service,
    ),
    session: AsyncSession = Depends(get_db),
):
    await validate_product_exists(
        product_id,
        session,
    )

    await service.delete_image(
        product_id,
        image_id,
    )