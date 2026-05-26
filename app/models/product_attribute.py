from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    product_attribute_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.product_id",
            ondelete="CASCADE",
        )
    )

    group_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
    )

    value: Mapped[str] = mapped_column(
        Text,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    product: Mapped["Product"] = relationship(
        back_populates="attributes",
    )