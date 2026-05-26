from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductStore(Base):
    __tablename__ = "product_to_store"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id", ondelete="CASCADE"),
        primary_key=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.store_id", ondelete="CASCADE"),
        primary_key=True,
    )

    product: Mapped["Product"] = relationship(
        back_populates="stores",
    )

    store: Mapped["Store"] = relationship(
        back_populates="products",
    )