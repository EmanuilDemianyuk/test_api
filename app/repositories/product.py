from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_attribute import (
    ProductAttribute,
)
from app.models.product_category import (
    ProductCategory,
)


class ProductRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create_product(
        self,
        payload: dict,
    ) -> Product:
        product = Product(**payload)

        self.session.add(product)

        await self.session.flush()

        return product

    async def get_products(
        self,
        page: int,
        size: int,
    ) -> tuple[list[dict], int]:

        stmt = (
            select(Product)
            .order_by(Product.product_id.asc())
            .options(
                selectinload(Product.categories)
                .selectinload(ProductCategory.category)
            )
            .limit(size)
            .offset((page - 1) * size)
        )

        result = await self.session.execute(stmt)
        products = result.scalars().unique().all()
    
        # total count (correct)
        total_stmt = select(func.count(Product.product_id))
        total = await self.session.scalar(total_stmt)
    
        items = []
    
        for product in products:
            items.append({
                "product_id": product.product_id,
                "name": product.name,
                "categories": [
                    pc.category.name
                    for pc in product.categories
                ],
                "price": product.price,
            })
    
        return items, total
    
    async def get_by_id(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.categories)
                .selectinload(ProductCategory.category)
                .selectinload(Category.parent),
                selectinload(Product.images),
                selectinload(Product.attributes),
            )
            .where(Product.product_id == product_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_seo_keyword(
        self,
        seo_keyword: str | None,
    ):
        if not seo_keyword:
            return None
    
        stmt = select(Product).where(
            Product.seo_keyword == seo_keyword
        )
    
        result = await self.session.execute(stmt)
    
        return result.scalar_one_or_none()