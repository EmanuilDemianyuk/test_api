from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

from app.core.enums import StatusEnum


class CategoryCreateSchema(BaseModel):
    name: str
    description: str | None = None

    parent_category_id: int | None = None

    seo_keyword: str | None = None

    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None

    image: str | None = None

    status: StatusEnum = StatusEnum.DISABLED


class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None

    parent_category_id: int | None = None

    seo_keyword: str | None = None

    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None

    image: str | None = None

    status: StatusEnum | None = None


class CategoryResponseSchema(BaseModel):
    category_id: int

    name: str

    full_path: str

    description: str | None

    parent_category_id: int | None

    seo_keyword: str | None

    meta_title: str | None
    meta_description: str | None
    meta_keyword: str | None

    image: str | None

    status: StatusEnum

    date_added: datetime
    date_modified: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CategoryListItemSchema(BaseModel):
    category_id: int

    full_path: str

    status: StatusEnum        