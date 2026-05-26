from pydantic import BaseModel, ConfigDict


class ProductStoreCreateSchema(BaseModel):
    store_id: int


class ProductStoreResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    store_id: int
    name: str