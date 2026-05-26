from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base
from app.utils.category_tree import build_full_path


class ProductCategory(Base):
    __tablename__ = "product_categories"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "category_id",
            name="uq_product_category",
        ),
    )

    product_category_id: Mapped[int] = mapped_column(
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

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.category_id",
            ondelete="CASCADE",
        )
    )

    product: Mapped["Product"] = relationship(
        back_populates="categories",
    )

    category: Mapped["Category"] = relationship()

    @property
    def category_name(self) -> str:
        return self.category.name if self.category else ""

    @property
    def full_path(self) -> str:
        if not self.category:
            return ""

        lookup = {}
        current = self.category

        while current is not None:
            lookup[current.category_id] = current
            current = current.parent

        return build_full_path(self.category, lookup)