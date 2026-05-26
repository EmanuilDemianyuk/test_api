import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.seeders import ensure_demo_data
from tests.seeders import cleanup_seed_data


@pytest.mark.asyncio
async def test_get_products_returns_seeded_demo_data(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50")

    assert response.status_code == 200

    body = response.json()

    assert body["page"] == 1
    assert body["size"] == 50
    assert body["total"] == 6

    assert {item["name"] for item in body["items"]} == {
        "Essential Cotton T-Shirt",
        "Fleece Hoodie",
        "Relaxed Linen Dress",
        "Trail Runner Sneakers",
        "Leather Crossbody Bag",
        "Ceramic Coffee Mug Set",
    }

    for item in body["items"]:
        assert item["product_id"] > 0
        assert isinstance(item["categories"], list)
        assert len(item["categories"]) >= 1
        assert item["price"] is not None
