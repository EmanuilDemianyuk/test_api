from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.core.enums import StatusEnum
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_attribute import ProductAttribute
from app.models.product_category import ProductCategory

from app.repositories.product import ProductRepository

from app.schemas.product import (
    ProductAttributeCreateSchema,
    ProductAttributeUpdateSchema,
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

    async def _validate_categories(self, category_ids: list[int]):
        if not category_ids:
            return

        result = await self.session.execute(
            select(Category.category_id).where(
                Category.category_id.in_(category_ids)
            )
        )

        existing_ids = set(result.scalars().all())
        missing = set(category_ids) - existing_ids
        
        if missing:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )


    async def _validate_duplicate_seo(
        self,
        seo_keyword: str | None,
    ):
        seo_keyword = (
            seo_keyword.strip()
            if isinstance(seo_keyword, str)
            else None
        )
    
        if not seo_keyword:
            return
    
        existing = await self.repository.get_by_seo_keyword(
            seo_keyword,
        )
    
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Product with this SEO keyword already exists",
            )

    async def create_product(
        self,
        payload: ProductCreateSchema,
    ):
        try:
            category_ids = [c.category_id for c in payload.categories]

            await self._validate_categories(category_ids)
            await self._validate_duplicate_seo(
                payload.seo_keyword
            )

            product_data = payload.model_dump(
                exclude={
                    "categories",
                    "images",
                    "attributes",
                }
            )

            product = await self.repository.create_product(product_data)

            self.session.add_all([
                ProductCategory(
                    product_id=product.product_id,
                    category_id=c.category_id,
                )
                for c in payload.categories
            ])

            self.session.add_all([
                ProductImage(
                    product_id=product.product_id,
                    **img.model_dump(),
                )
                for img in payload.images
            ])

            self.session.add_all([
                ProductAttribute(
                    product_id=product.product_id,
                    **attr.model_dump(),
                )
                for attr in payload.attributes
            ])

            await self.session.commit()

            return await self.repository.get_by_id(product.product_id)

        except Exception:
            await self.session.rollback()
            raise

    async def get_products(
        self,
        page: int,
        size: int,
        category_ids: list[int] | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        status: StatusEnum | None = None,
    ):
        return await self.repository.get_products(
            page=page,
            size=size,
            category_ids=category_ids,
            min_price=min_price,
            max_price=max_price,
            status=status,
        )

    async def _ensure_product_exists(
        self,
        product_id: int,
    ) -> Product:
        product = await self.repository.get_by_id(
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return product

    async def get_product_attributes(
        self,
        product_id: int,
    ):
        await self._ensure_product_exists(product_id)

        result = await self.session.execute(
            select(ProductAttribute)
            .where(ProductAttribute.product_id == product_id)
            .order_by(
                ProductAttribute.sort_order.asc(),
                ProductAttribute.product_attribute_id.asc(),
            )
        )

        return result.scalars().all()

    async def create_product_attribute(
        self,
        product_id: int,
        payload: ProductAttributeCreateSchema,
    ):
        await self._ensure_product_exists(product_id)

        try:
            attribute = ProductAttribute(
                product_id=product_id,
                **payload.model_dump(),
            )

            self.session.add(attribute)
            await self.session.commit()
            await self.session.refresh(attribute)

            return attribute

        except Exception:
            await self.session.rollback()
            raise

    async def _get_product_attribute(
        self,
        product_id: int,
        attribute_id: int,
    ) -> ProductAttribute:
        await self._ensure_product_exists(product_id)

        attribute = await self.session.scalar(
            select(ProductAttribute).where(
                ProductAttribute.product_id == product_id,
                ProductAttribute.product_attribute_id == attribute_id,
            )
        )

        if not attribute:
            raise HTTPException(
                status_code=404,
                detail="Attribute not found",
            )

        return attribute

    async def update_product_attribute(
        self,
        product_id: int,
        attribute_id: int,
        payload: ProductAttributeUpdateSchema,
    ):
        attribute = await self._get_product_attribute(
            product_id,
            attribute_id,
        )

        try:
            update_data = payload.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(attribute, key, value)

            await self.session.commit()
            await self.session.refresh(attribute)

            return attribute

        except Exception:
            await self.session.rollback()
            raise

    async def delete_product_attribute(
        self,
        product_id: int,
        attribute_id: int,
    ):
        attribute = await self._get_product_attribute(
            product_id,
            attribute_id,
        )

        try:
            await self.session.delete(attribute)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def get_product_categories(
        self,
        product_id: int,
    ):
        await self._ensure_product_exists(product_id)

        result = await self.session.execute(
            select(ProductCategory)
            .options(selectinload(ProductCategory.category))
            .where(ProductCategory.product_id == product_id)
        )

        return result.scalars().all()

    async def create_product_category(
        self,
        product_id: int,
        category_id: int,
    ):
        product = await self.repository.get_by_id(
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        await self._validate_categories([category_id])

        existing_assignment = await self.session.scalar(
            select(ProductCategory).where(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
            )
        )

        if existing_assignment:
            raise HTTPException(
                status_code=409,
                detail="Category already assigned",
            )

        try:
            product_category = ProductCategory(
                product_id=product_id,
                category_id=category_id,
            )

            self.session.add(product_category)
            await self.session.commit()
            await self.session.refresh(product_category)

            return product_category

        except Exception:
            await self.session.rollback()
            raise

    async def delete_product_category(
        self,
        product_id: int,
        category_id: int,
    ):
        product = await self.repository.get_by_id(
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        product_category = await self.session.scalar(
            select(ProductCategory).where(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
            )
        )

        if not product_category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        try:
            await self.session.delete(product_category)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def update_product(
        self,
        product: Product,
        payload: ProductUpdateSchema,
    ):
        try:
            update_data = payload.model_dump(exclude_unset=True)

            categories = update_data.pop("categories", None)

            # ---- categories update ----
            if categories is not None:
                category_ids = [c["category_id"] for c in categories]

                await self._validate_categories(category_ids)

                await self.session.execute(
                    delete(ProductCategory).where(
                        ProductCategory.product_id == product.product_id
                )
)

                self.session.add_all([
                    ProductCategory(
                        product_id=product.product_id,
                        category_id=c["category_id"],
                    )
                    for c in categories
                ])

            # ---- duplicate SEO check ----
            if "seo_keyword" in update_data:
                await self._validate_duplicate_seo(
                    update_data["seo_keyword"]
                )

            # ---- update fields ----
            for key, value in update_data.items():
                setattr(product, key, value)

            await self.session.commit()
            await self.session.refresh(product)

            return await self.repository.get_by_id(product.product_id)

        except Exception:
            await self.session.rollback()
            raise

    async def delete_product(
        self,
        product: Product,
    ):
        try:
            await self.session.delete(product)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise