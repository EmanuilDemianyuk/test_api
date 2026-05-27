import pytest
from decimal import Decimal
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.enums import StatusEnum
from app.seeders import ensure_demo_data
from tests.seeders import cleanup_seed_data


@pytest.mark.asyncio
async def test_filter_by_price_min(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&min_price=50")

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        assert item["price"] is None or Decimal(str(item["price"])) >= Decimal("50")


@pytest.mark.asyncio
async def test_filter_by_price_max(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&max_price=50")

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        assert item["price"] is None or Decimal(str(item["price"])) <= Decimal("50")


@pytest.mark.asyncio
async def test_filter_by_price_range(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&min_price=15&max_price=60")

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        if item["price"] is not None:
            price = Decimal(str(item["price"]))
            assert price >= Decimal("15")
            assert price <= Decimal("60")


@pytest.mark.asyncio
async def test_filter_by_status(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&status=1")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0


@pytest.mark.asyncio
async def test_filter_by_category_id(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&category_id=1")

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        assert any(cat for cat in item["categories"])


@pytest.mark.asyncio
async def test_filter_by_multiple_category_ids(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&category_id=1&category_id=2")

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        assert any(cat for cat in item["categories"])


@pytest.mark.asyncio
async def test_combined_filters(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/product?page=1&size=50&min_price=15&max_price=100&status=1&category_id=1"
        )

    assert response.status_code == 200
    body = response.json()
    
    for item in body["items"]:
        if item["price"] is not None:
            price = Decimal(str(item["price"]))
            assert price >= Decimal("15")
            assert price <= Decimal("100")
        assert any(cat for cat in item["categories"])


@pytest.mark.asyncio
async def test_no_results_for_impossible_filter(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&min_price=10000&max_price=20000")

    assert response.status_code == 200
    body = response.json()
    
    assert body["total"] == 0
    assert len(body["items"]) == 0
