from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Text,
    Enum,
    Numeric,
    Float,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import StatusEnum
from app.models.base import Base
from app.models.mixins import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    seo_keyword: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    meta_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    meta_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    meta_keyword: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        default=StatusEnum.DISABLED,
        nullable=False,
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    manufacturer_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    rating: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    viewed: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    categories: Mapped[list["ProductCategory"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    attributes: Mapped[list["ProductAttribute"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )