from fastapi import HTTPException, status

from app.repositories.product_store import ProductStoreRepository


class ProductStoreService:
    def __init__(self, session):
        self.session = session
        self.repository = ProductStoreRepository(session)

    async def get_product_stores(self, product_id: int):
        product = await self.repository.get_product_with_stores(product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return [
            {
                "store_id": relation.store.store_id,
                "name": relation.store.name,
            }
            for relation in product.stores
        ]

    async def add_store_to_product(
        self,
        product_id: int,
        store_id: int,
    ):
        product = await self.repository.get_product_with_stores(product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        store = await self.repository.get_store(store_id)

        if not store:
            raise HTTPException(
                status_code=404,
                detail="Store not found",
            )

        if any(s.store_id == store_id for s in product.stores):
            raise HTTPException(
                status_code=409,
                detail="Store already attached to product",
            )

        await self.repository.add_store_to_product(
            product_id=product_id,
            store_id=store_id,
        )

        await self.session.commit()

        return {"message": "Store added to product"}

    async def delete_store_from_product(
        self,
        product_id: int,
        store_id: int,
    ):
        product = await self.repository.get_product_with_stores(product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        relation_exists = any(
            s.store_id == store_id
            for s in product.stores
        )

        if not relation_exists:
            raise HTTPException(
                status_code=404,
                detail="Store relation not found",
            )

        await self.repository.delete_store_from_product(
            product_id=product_id,
            store_id=store_id,
        )

        await self.session.commit()

        return {"message": "Store removed from product"}