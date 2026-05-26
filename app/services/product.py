from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_attribute import ProductAttribute
from app.models.product_category import ProductCategory

from app.repositories.product import ProductRepository

from app.schemas.product import (
    ProductCreateSchema,
    ProductUpdateSchema,
)


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        session: AsyncSession,
    ):
        self.repository = repository

        self.session = session

    async def create_product(
        self,
        payload: ProductCreateSchema,
    ):
        try:
            product_data = payload.model_dump(
                exclude={
                    "categories",
                    "images",
                    "attributes",
                }
            )

            product = await self.repository.create_product(
                product_data
            )

            for category_data in payload.categories:
                self.session.add(
                    ProductCategory(
                        product_id=product.product_id,
                        category_id=category_data.category_id,
                    )
                )

            for image_data in payload.images:
                self.session.add(
                    ProductImage(
                        product_id=product.product_id,
                        **image_data.model_dump(),
                    )
                )

            for attr_data in payload.attributes:
                self.session.add(
                    ProductAttribute(
                        product_id=product.product_id,
                        **attr_data.model_dump(),
                    )
                )

            await self.session.commit()

            await self.session.refresh(product)

            return await self.repository.get_by_id(
                product.product_id
            )

        except IntegrityError as exc:
            await self.session.rollback()
            message = str(exc.orig).lower()
            if "duplicate" in message or "unique" in message:
                raise HTTPException(
                    status_code=409,
                    detail="Product with this SEO keyword already exists",
                )
            raise

        except Exception:
            await self.session.rollback()
            raise

    async def get_products(
        self,
        page: int,
        size: int,
    ):
        return await self.repository.get_products(
            page=page,
            size=size,
        )
        
    async def update_product(
        self,
        product: Product,
        payload: ProductUpdateSchema,
    ):
        try:
            update_data = payload.model_dump(
                exclude_unset=True,
            )

            categories = update_data.pop("categories", None)

            if categories is not None:
                for product_category in list(product.categories):
                    await self.session.delete(product_category)

                for category_data in categories:
                    category = await self.session.get(
                        Category,
                        category_data["category_id"],
                    )

                    if category is None:
                        raise HTTPException(
                            status_code=404,
                            detail="Category not found",
                        )

                    self.session.add(
                        ProductCategory(
                            product_id=product.product_id,
                            category_id=category.category_id,
                        )
                    )

            for key, value in update_data.items():
                setattr(product, key, value)

            await self.session.commit()
            await self.session.refresh(product)

            return await self.repository.get_by_id(
                product.product_id,
            )

        except IntegrityError as exc:
            await self.session.rollback()
            message = str(exc.orig).lower()
            if "duplicate" in message or "unique" in message:
                raise HTTPException(
                    status_code=409,
                    detail="Product with this SEO keyword already exists",
                )
            raise

        except Exception:
            await self.session.rollback()
            raise
    
    async def delete_product(
        self,
        product: Product,
    ):
        await self.session.delete(product)
        await self.session.commit()