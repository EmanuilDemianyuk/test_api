from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import StatusEnum
from app.models.category import Category
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.product_category import ProductCategory
from app.models.product_image import ProductImage
from app.repositories.category import CategoryRepository


CATEGORY_SEED_DATA = [
    {
        "name": "Demo Store",
        "description": "A realistic demo storefront root category for local testing.",
        "seo_keyword": "demo-root-category",
        "meta_title": "Demo Store",
        "meta_description": "Root category for seeded demo catalog data.",
        "meta_keyword": "demo, store, seed",
        "image": "https://images.example.com/demo-store-root.jpg",
        "parent_seo": None,
    },
    {
        "name": "Men's Clothing",
        "description": "Seasonal essentials for men including tees, hoodies, and basics.",
        "seo_keyword": "demo-men-clothing-category",
        "meta_title": "Men's Clothing",
        "meta_description": "Men's clothing collection for demo data.",
        "meta_keyword": "demo, men's clothing, apparel",
        "image": "https://images.example.com/demo-men-clothing.jpg",
        "parent_seo": "demo-root-category",
    },
    {
        "name": "Women's Clothing",
        "description": "Soft, modern silhouettes and everyday basics for women.",
        "seo_keyword": "demo-women-clothing-category",
        "meta_title": "Women's Clothing",
        "meta_description": "Women's clothing collection for demo data.",
        "meta_keyword": "demo, women's clothing, apparel",
        "image": "https://images.example.com/demo-women-clothing.jpg",
        "parent_seo": "demo-root-category",
    },
    {
        "name": "Footwear",
        "description": "Performance and everyday footwear for all occasions.",
        "seo_keyword": "demo-footwear-category",
        "meta_title": "Footwear",
        "meta_description": "Footwear collection for demo data.",
        "meta_keyword": "demo, footwear, sneakers, shoes",
        "image": "https://images.example.com/demo-footwear.jpg",
        "parent_seo": "demo-root-category",
    },
    {
        "name": "Accessories",
        "description": "Practical accessories that complement everyday outfits.",
        "seo_keyword": "demo-accessories-category",
        "meta_title": "Accessories",
        "meta_description": "Accessories collection for demo data.",
        "meta_keyword": "demo, accessories, bags",
        "image": "https://images.example.com/demo-accessories.jpg",
        "parent_seo": "demo-root-category",
    },
    {
        "name": "Home & Living",
        "description": "Everyday items for the home with premium finishes.",
        "seo_keyword": "demo-home-living-category",
        "meta_title": "Home & Living",
        "meta_description": "Home and living collection for demo data.",
        "meta_keyword": "demo, home, living, decor",
        "image": "https://images.example.com/demo-home-living.jpg",
        "parent_seo": "demo-root-category",
    },
]

PRODUCT_SEED_DATA = [
    {
        "name": "Essential Cotton T-Shirt",
        "description": "A soft, breathable cotton tee with a clean fit and everyday versatility.",
        "seo_keyword": "demo-essential-cotton-tshirt",
        "meta_title": "Essential Cotton T-Shirt",
        "meta_description": "Premium cotton tee for everyday wear.",
        "meta_keyword": "demo, cotton, t-shirt, essentials",
        "image": "https://images.example.com/demo-essential-cotton-tshirt.jpg",
        "price": 24.9,
        "model": "CT-1001",
        "manufacturer_id": 1,
        "rating": 4.7,
        "viewed": 1485,
        "category_seo": "demo-men-clothing-category",
        "images": [
            "https://images.example.com/demo-essential-cotton-tshirt-1.jpg",
            "https://images.example.com/demo-essential-cotton-tshirt-2.jpg",
            "https://images.example.com/demo-essential-cotton-tshirt-3.jpg",
        ],
        "attributes": [
            {"group_name": "Fit", "name": "Size", "value": "M", "sort_order": 0},
            {"group_name": "Details", "name": "Color", "value": "Slate Blue", "sort_order": 1},
            {"group_name": "Material", "name": "Fabric", "value": "100% cotton", "sort_order": 2},
            {"group_name": "Care", "name": "Wash", "value": "Machine washable", "sort_order": 3},
        ],
    },
    {
        "name": "Fleece Hoodie",
        "description": "A cozy fleece hoodie with a relaxed cut and practical kangaroo pocket.",
        "seo_keyword": "demo-fleece-hoodie",
        "meta_title": "Fleece Hoodie",
        "meta_description": "Warm fleece hoodie with modern details.",
        "meta_keyword": "demo, hoodie, fleece, menswear",
        "image": "https://images.example.com/demo-fleece-hoodie.jpg",
        "price": 49.9,
        "model": "FH-2044",
        "manufacturer_id": 1,
        "rating": 4.8,
        "viewed": 2120,
        "category_seo": "demo-men-clothing-category",
        "images": [
            "https://images.example.com/demo-fleece-hoodie-1.jpg",
            "https://images.example.com/demo-fleece-hoodie-2.jpg",
        ],
        "attributes": [
            {"group_name": "Fit", "name": "Size", "value": "L", "sort_order": 0},
            {"group_name": "Details", "name": "Color", "value": "Charcoal", "sort_order": 1},
            {"group_name": "Features", "name": "Pockets", "value": "Kangaroo pocket", "sort_order": 2},
            {"group_name": "Material", "name": "Fabric", "value": "Fleece lined", "sort_order": 3},
        ],
    },
    {
        "name": "Relaxed Linen Dress",
        "description": "A lightweight linen dress designed for easy layering and a polished everyday look.",
        "seo_keyword": "demo-relaxed-linen-dress",
        "meta_title": "Relaxed Linen Dress",
        "meta_description": "Breathable linen dress with an elegant silhouette.",
        "meta_keyword": "demo, dress, linen, women",
        "image": "https://images.example.com/demo-relaxed-linen-dress.jpg",
        "price": 59.9,
        "model": "LD-3308",
        "manufacturer_id": 2,
        "rating": 4.6,
        "viewed": 1725,
        "category_seo": "demo-women-clothing-category",
        "images": [
            "https://images.example.com/demo-relaxed-linen-dress-1.jpg",
            "https://images.example.com/demo-relaxed-linen-dress-2.jpg",
            "https://images.example.com/demo-relaxed-linen-dress-3.jpg",
        ],
        "attributes": [
            {"group_name": "Fit", "name": "Size", "value": "S", "sort_order": 0},
            {"group_name": "Details", "name": "Color", "value": "Sand", "sort_order": 1},
            {"group_name": "Material", "name": "Fabric", "value": "Linen blend", "sort_order": 2},
            {"group_name": "Style", "name": "Length", "value": "Knee-length", "sort_order": 3},
        ],
    },
    {
        "name": "Trail Runner Sneakers",
        "description": "Lightweight running sneakers with cushioned support for daily training and errands.",
        "seo_keyword": "demo-trail-runner-sneakers",
        "meta_title": "Trail Runner Sneakers",
        "meta_description": "Cushioned running sneakers with easy movement support.",
        "meta_keyword": "demo, sneakers, running, trail",
        "image": "https://images.example.com/demo-trail-runner-sneakers.jpg",
        "price": 89.9,
        "model": "TR-5512",
        "manufacturer_id": 3,
        "rating": 4.9,
        "viewed": 2860,
        "category_seo": "demo-footwear-category",
        "images": [
            "https://images.example.com/demo-trail-runner-sneakers-1.jpg",
            "https://images.example.com/demo-trail-runner-sneakers-2.jpg",
        ],
        "attributes": [
            {"group_name": "Fit", "name": "Size", "value": "42", "sort_order": 0},
            {"group_name": "Details", "name": "Color", "value": "Ocean Green", "sort_order": 1},
            {"group_name": "Support", "name": "Midsole", "value": "Gel cushioning", "sort_order": 2},
            {"group_name": "Use", "name": "Activity", "value": "Running & walking", "sort_order": 3},
        ],
    },
    {
        "name": "Leather Crossbody Bag",
        "description": "A compact leather crossbody bag with a secure zip compartment and soft lining.",
        "seo_keyword": "demo-leather-crossbody-bag",
        "meta_title": "Leather Crossbody Bag",
        "meta_description": "Premium crossbody bag with everyday organization.",
        "meta_keyword": "demo, leather, bag, accessories",
        "image": "https://images.example.com/demo-leather-crossbody-bag.jpg",
        "price": 79.9,
        "model": "CB-7721",
        "manufacturer_id": 4,
        "rating": 4.7,
        "viewed": 1978,
        "category_seo": "demo-accessories-category",
        "images": [
            "https://images.example.com/demo-leather-crossbody-bag-1.jpg",
            "https://images.example.com/demo-leather-crossbody-bag-2.jpg",
        ],
        "attributes": [
            {"group_name": "Details", "name": "Color", "value": "Black", "sort_order": 0},
            {"group_name": "Material", "name": "Leather", "value": "Full-grain", "sort_order": 1},
            {"group_name": "Storage", "name": "Compartments", "value": "2 zip pockets", "sort_order": 2},
            {"group_name": "Fit", "name": "Strap", "value": "Adjustable crossbody", "sort_order": 3},
        ],
    },
    {
        "name": "Ceramic Coffee Mug Set",
        "description": "A ceramic mug set with a matte finish and a premium feel for everyday mornings.",
        "seo_keyword": "demo-ceramic-coffee-mug-set",
        "meta_title": "Ceramic Coffee Mug Set",
        "meta_description": "Ceramic mug set for home and gifting.",
        "meta_keyword": "demo, mug, ceramic, home",
        "image": "https://images.example.com/demo-ceramic-coffee-mug-set.jpg",
        "price": 34.9,
        "model": "CM-8813",
        "manufacturer_id": 5,
        "rating": 4.5,
        "viewed": 1380,
        "category_seo": "demo-home-living-category",
        "images": [
            "https://images.example.com/demo-ceramic-coffee-mug-set-1.jpg",
            "https://images.example.com/demo-ceramic-coffee-mug-set-2.jpg",
        ],
        "attributes": [
            {"group_name": "Details", "name": "Capacity", "value": "350 ml", "sort_order": 0},
            {"group_name": "Material", "name": "Finish", "value": "Matte ceramic", "sort_order": 1},
            {"group_name": "Care", "name": "Dishwasher safe", "value": "Yes", "sort_order": 2},
            {"group_name": "Set", "name": "Includes", "value": "2 mugs", "sort_order": 3},
        ],
    },
]


async def has_existing_app_data(session: AsyncSession) -> bool:
    category_count = await session.scalar(
        select(func.count()).select_from(Category)
    )
    product_count = await session.scalar(
        select(func.count()).select_from(Product)
    )

    return bool(category_count or product_count)


async def seed_demo_data(session: AsyncSession) -> bool:
    if await has_existing_app_data(session):
        return False

    repository = CategoryRepository(session)
    categories = {}

    for category_payload in CATEGORY_SEED_DATA:
        parent_category_id = None

        if category_payload["parent_seo"] is not None:
            parent_category_id = categories[category_payload["parent_seo"]].category_id

        category_data = {
            key: value
            for key, value in category_payload.items()
            if key != "parent_seo"
        }

        category = await repository.create(
            {
                **category_data,
                "status": StatusEnum.ENABLED,
                "parent_category_id": parent_category_id,
            }
        )
        categories[category_payload["seo_keyword"]] = category

    for product_payload in PRODUCT_SEED_DATA:
        product = Product(
            name=product_payload["name"],
            description=product_payload["description"],
            seo_keyword=product_payload["seo_keyword"],
            meta_title=product_payload["meta_title"],
            meta_description=product_payload["meta_description"],
            meta_keyword=product_payload["meta_keyword"],
            image=product_payload["image"],
            status=StatusEnum.ENABLED,
            price=product_payload["price"],
            model=product_payload["model"],
            manufacturer_id=product_payload["manufacturer_id"],
            rating=product_payload["rating"],
            viewed=product_payload["viewed"],
        )

        session.add(product)
        await session.flush()

        related_entities = [
            ProductCategory(
                product_id=product.product_id,
                category_id=categories[product_payload["category_seo"]].category_id,
            )
        ]

        related_entities.extend(
            ProductImage(
                product_id=product.product_id,
                image=image_url,
                sort_order=index,
            )
            for index, image_url in enumerate(product_payload["images"])
        )

        related_entities.extend(
            ProductAttribute(
                product_id=product.product_id,
                group_name=attribute["group_name"],
                name=attribute["name"],
                value=attribute["value"],
                sort_order=attribute["sort_order"],
            )
            for attribute in product_payload["attributes"]
        )

        session.add_all(related_entities)

    await session.commit()

    return True


async def ensure_demo_data(session: AsyncSession) -> bool:
    if await has_existing_app_data(session):
        return False

    return await seed_demo_data(session)
