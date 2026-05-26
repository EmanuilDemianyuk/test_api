from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    Enum,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import StatusEnum
from app.models.base import Base
from app.models.mixins import TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    __table_args__ = (
        Index(
            "ix_categories_parent_category_id",
            "parent_category_id",
        ),
    )

    category_id: Mapped[int] = mapped_column(
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

    parent_category_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "categories.category_id",
            ondelete="CASCADE",
        ),
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

    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[category_id],
        backref="children",
        passive_deletes=True,
    )