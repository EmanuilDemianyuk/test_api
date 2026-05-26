import pytest
from sqlalchemy import func, select

from app.models.category import Category
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.product_category import ProductCategory
from app.models.product_image import ProductImage
from app.seeders import ensure_demo_data
from tests.seeders import cleanup_seed_data


@pytest.mark.asyncio
async def test_ensure_demo_data_creates_realistic_catalog(db_session):
    await cleanup_seed_data(db_session)

    created = await ensure_demo_data(db_session)

    assert created is True

    root_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-root-category")
    )
    men_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-men-clothing-category")
    )
    women_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-women-clothing-category")
    )
    footwear_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-footwear-category")
    )
    accessories_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-accessories-category")
    )
    home_category = await db_session.scalar(
        select(Category).where(Category.seo_keyword == "demo-home-living-category")
    )

    tshirt_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-essential-cotton-tshirt")
    )
    hoodie_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-fleece-hoodie")
    )
    dress_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-relaxed-linen-dress")
    )
    sneakers_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-trail-runner-sneakers")
    )
    bag_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-leather-crossbody-bag")
    )
    mug_product = await db_session.scalar(
        select(Product).where(Product.seo_keyword == "demo-ceramic-coffee-mug-set")
    )

    assert root_category is not None
    assert men_category is not None
    assert women_category is not None
    assert footwear_category is not None
    assert accessories_category is not None
    assert home_category is not None

    assert men_category.parent_category_id == root_category.category_id
    assert women_category.parent_category_id == root_category.category_id
    assert footwear_category.parent_category_id == root_category.category_id
    assert accessories_category.parent_category_id == root_category.category_id
    assert home_category.parent_category_id == root_category.category_id

    assert tshirt_product is not None
    assert hoodie_product is not None
    assert dress_product is not None
    assert sneakers_product is not None
    assert bag_product is not None
    assert mug_product is not None

    for product in (
        tshirt_product,
        hoodie_product,
        dress_product,
        sneakers_product,
        bag_product,
        mug_product,
    ):
        category_link = await db_session.scalar(
            select(func.count())
            .select_from(ProductCategory)
            .where(ProductCategory.product_id == product.product_id)
        )
        image_count = await db_session.scalar(
            select(func.count())
            .select_from(ProductImage)
            .where(ProductImage.product_id == product.product_id)
        )
        attribute_count = await db_session.scalar(
            select(func.count())
            .select_from(ProductAttribute)
            .where(ProductAttribute.product_id == product.product_id)
        )

        assert category_link == 1
        assert image_count >= 2
        assert attribute_count >= 2

    second_run = await ensure_demo_data(db_session)

    assert second_run is False

    category_count = await db_session.scalar(
        select(func.count()).select_from(Category)
    )
    product_count = await db_session.scalar(
        select(func.count()).select_from(Product)
    )

    assert category_count == 6
    assert product_count == 6
