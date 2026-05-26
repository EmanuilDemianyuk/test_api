from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    product_image_id: Mapped[int] = mapped_column(
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

    image: Mapped[str] = mapped_column(
        String(500),
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    product: Mapped["Product"] = relationship(
        back_populates="images",
    )