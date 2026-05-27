from decimal import Decimal
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import StatusEnum, SortByEnum, SortOrderEnum
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
        category_ids: list[int] | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        status: StatusEnum | None = None,
        sort_by: SortByEnum | None = None,
        sort_order: SortOrderEnum | None = None,
    ) -> tuple[list[dict], int]:

        stmt = select(Product)

        if category_ids:
            stmt = (
                stmt
                .join(ProductCategory)
                .where(ProductCategory.category_id.in_(category_ids))
            )

        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)

        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)

        if status is not None:
            stmt = stmt.where(Product.status == status)

        # Determine sort column
        sort_col = Product.product_id
        if sort_by == SortByEnum.NAME:
            sort_col = Product.name
        elif sort_by == SortByEnum.PRICE:
            sort_col = Product.price
        elif sort_by == SortByEnum.CATEGORY:
            # For category sorting, join and sort by category name
            if not category_ids:
                stmt = stmt.join(ProductCategory)
            stmt = stmt.join(Category, ProductCategory.category_id == Category.category_id)
            sort_col = Category.name
        elif sort_by == SortByEnum.DATE_ADDED:
            sort_col = Product.date_added

        # Determine sort direction
        if sort_order == SortOrderEnum.DESC:
            sort_col = sort_col.desc()
        else:
            sort_col = sort_col.asc()

        stmt = (
            stmt
            .order_by(sort_col)
            .options(
                selectinload(Product.categories)
                .selectinload(ProductCategory.category)
            )
            .limit(size)
            .offset((page - 1) * size)
        )

        result = await self.session.execute(stmt)
        products = result.scalars().unique().all()
    
        # total count with filters
        total_stmt = select(func.count(Product.product_id.distinct()))

        if category_ids:
            total_stmt = (
                total_stmt
                .join(ProductCategory)
                .where(ProductCategory.category_id.in_(category_ids))
            )

        if min_price is not None:
            total_stmt = total_stmt.where(Product.price >= min_price)

        if max_price is not None:
            total_stmt = total_stmt.where(Product.price <= max_price)

        if status is not None:
            total_stmt = total_stmt.where(Product.status == status)

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