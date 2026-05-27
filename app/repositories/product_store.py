from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.store import Store
from app.models.product_store import ProductStore


class ProductStoreRepository:
    def __init__(self, session):
        self.session = session

    async def get_product_with_stores(self, product_id: int):
        query = (
            select(Product)
            .options(
                selectinload(Product.stores)
                .selectinload(ProductStore.store)
            )
            .where(Product.product_id == product_id)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_store(self, store_id: int):
        query = select(Store).where(Store.store_id == store_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_store_to_product(
        self,
        product_id: int,
        store_id: int,
    ):
        relation = ProductStore(
            product_id=product_id,
            store_id=store_id,
        )

        self.session.add(relation)

    async def delete_store_from_product(
        self,
        product_id: int,
        store_id: int,
    ):
        query = delete(ProductStore).where(
            ProductStore.product_id == product_id,
            ProductStore.store_id == store_id,
        )

        await self.session.execute(query)