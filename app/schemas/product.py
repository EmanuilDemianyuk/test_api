from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.core.enums import StatusEnum


class ProductImageCreateSchema(BaseModel):
    image: str
    sort_order: int = 0


class ProductImageResponseSchema(
    ProductImageCreateSchema,
):
    product_image_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductAttributeCreateSchema(BaseModel):
    group_name: str |None = None

    name: str

    value: str

    sort_order: int = 0


class ProductAttributeUpdateSchema(BaseModel):
    group_name: str | None = None

    name: str | None = None

    value: str | None = None

    sort_order: int | None = None


class ProductAttributeResponseSchema(
    ProductAttributeCreateSchema,
):
    product_attribute_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductCategoryCreateSchema(BaseModel):
    category_id: int


class ProductCategoryResponseSchema(BaseModel):
    product_category_id: int

    category_id: int

    category_name: str

    full_path: str

    model_config = ConfigDict(from_attributes=True)


class StoreResponseSchema(BaseModel):
    store_id: int

    name: str

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    name: str

    description: str | None = None

    seo_keyword: str | None = None

    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None

    image: str | None = None

    status: StatusEnum = StatusEnum.DISABLED

    price: Decimal | None = None

    model: str | None = None

    manufacturer_id: int | None = None

    categories: list[
        ProductCategoryCreateSchema
    ] = Field(default_factory=list)

    images: list[
        ProductImageCreateSchema
    ] = Field(default_factory=list)

    attributes: list[
        ProductAttributeCreateSchema
    ] = Field(default_factory=list)


class ProductUpdateSchema(BaseModel):
    name: str | None = None

    description: str | None = None

    seo_keyword: str | None = None

    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None

    image: str | None = None

    status: StatusEnum | None = None

    price: Decimal | None = None

    model: str | None = None

    manufacturer_id: int | None = None

    categories: list[
        ProductCategoryCreateSchema
    ] | None = None


class ProductListItemSchema(BaseModel):
    product_id: int

    name: str

    categories: list[str]

    price: Decimal | None


class ProductDetailSchema(BaseModel):
    product_id: int

    name: str

    description: str | None

    seo_keyword: str | None

    meta_title: str | None
    meta_description: str | None
    meta_keyword: str | None

    image: str | None

    status: StatusEnum

    price: Decimal | None

    model: str | None

    manufacturer_id: int | None

    rating: float

    viewed: int

    date_added: datetime | None
    date_modified: datetime | None

    categories: list[
        ProductCategoryResponseSchema
    ] = Field(default_factory=list)

    images: list[
        ProductImageResponseSchema
    ] = Field(default_factory=list)

    attributes: list[
        ProductAttributeResponseSchema
    ] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    