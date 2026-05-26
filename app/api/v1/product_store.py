from fastapi import APIRouter, Depends, status

from app.core.db import get_db
from app.schemas.product_store import (
    ProductStoreCreateSchema,
    ProductStoreResponseSchema,
)
from app.services.product_store import ProductStoreService

router = APIRouter(prefix="/product", tags=["Product Stores"])


@router.get(
    "/{id}/store",
    response_model=list[ProductStoreResponseSchema],
)
async def get_product_stores(
    id: int,
    session=Depends(get_db),
):
    service = ProductStoreService(session)

    return await service.get_product_stores(id)


@router.post(
    "/{id}/store",
    status_code=status.HTTP_201_CREATED,
)
async def add_store_to_product(
    id: int,
    payload: ProductStoreCreateSchema,
    session=Depends(get_db),
):
    service = ProductStoreService(session)

    return await service.add_store_to_product(
        product_id=id,
        store_id=payload.store_id,
    )


@router.delete(
    "/{id}/store/{store_id}",
)
async def delete_store_from_product(
    id: int,
    store_id: int,
    session=Depends(get_db),
):
    service = ProductStoreService(session)

    return await service.delete_store_from_product(
        product_id=id,
        store_id=store_id,
    )