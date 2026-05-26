from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_product_images(
        self,
        product_id: int,
    ):
        stmt = (
            select(ProductImage)
            .where(
                ProductImage.product_id
                == product_id
            )
            .order_by(
                ProductImage.sort_order.asc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    
    async def get_product_image(
        self,
        product_id: int,
        image_id: int,
    ) -> ProductImage | None:
        stmt = (
            select(ProductImage)
            .where(
                ProductImage.product_id
                == product_id,
                ProductImage.product_image_id
                == image_id,
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def create_image(
        self,
        product_id: int,
        payload: dict,
    ) -> ProductImage:
        image = ProductImage(
            product_id=product_id,
            **payload,
        )

        self.session.add(image)

        await self.session.flush()

        await self.session.refresh(image)

        return image
    
    async def delete_image(
        self,
        image: ProductImage,
    ):
        await self.session.delete(image)