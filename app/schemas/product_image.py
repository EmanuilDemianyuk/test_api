from pydantic import BaseModel, ConfigDict


class ProductImageCreateSchema(BaseModel):
    image: str
    sort_order: int = 0


class ProductImageResponseSchema(ProductImageCreateSchema):
    product_image_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)