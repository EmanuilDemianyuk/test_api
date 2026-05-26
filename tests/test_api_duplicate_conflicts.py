import pytest
from httpx import ASGITransport, AsyncClient

from app.core.enums import StatusEnum
from app.main import app
from app.models.category import Category


@pytest.mark.asyncio
async def test_create_category_returns_conflict_for_duplicate_seo_keyword(db_session):
    existing = Category(
        name="Existing category",
        seo_keyword="duplicate-category-seo",
        status=StatusEnum.ENABLED,
    )
    db_session.add(existing)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/category",
            json={
                "name": "New category",
                "description": "Should conflict",
                "parent_category_id": None,
                "seo_keyword": "duplicate-category-seo",
                "meta_title": "New category",
                "meta_description": "conflict",
                "meta_keyword": "conflict",
                "image": "https://example.com/category.png",
                "status": 1,
            },
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Category with this SEO keyword already exists"
