from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_image import (
    ProductImageRepository,
)

from app.schemas.product_image import (
    ProductImageCreateSchema,
)


class ProductImageService:
    def __init__(
        self,
        repository: ProductImageRepository,
        session: AsyncSession,
    ):
        self.repository = repository

        self.session = session

    async def get_product_images(
        self,
        product_id: int,
    ):
        return await self.repository.get_product_images(
            product_id
        )
    
    async def create_image(
        self,
        product_id: int,
        payload: ProductImageCreateSchema,
    ):
        try:
            image = await self.repository.create_image(
                product_id,
                payload.model_dump(),
            )

            await self.session.commit()

            return image

        except Exception:
            await self.session.rollback()
            raise

    async def delete_image(
        self,
        product_id: int,
        image_id: int,
    ):
        image = await (
            self.repository.get_product_image(
                product_id,
                image_id,
            )
        )

        if not image:
            raise HTTPException(
                status_code=404,
                detail="Image not found",
            )

        try:
            await self.repository.delete_image(
                image,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise