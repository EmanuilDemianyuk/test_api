import pytest
from decimal import Decimal
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.seeders import ensure_demo_data
from tests.seeders import cleanup_seed_data


@pytest.mark.asyncio
async def test_sort_by_name_asc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=name&sort_order=asc")

    assert response.status_code == 200
    body = response.json()
    
    names = [item["name"] for item in body["items"]]
    assert names == sorted(names), "Names should be sorted in ascending order"


@pytest.mark.asyncio
async def test_sort_by_name_desc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=name&sort_order=desc")

    assert response.status_code == 200
    body = response.json()
    
    names = [item["name"] for item in body["items"]]
    assert names == sorted(names, reverse=True), "Names should be sorted in descending order"


@pytest.mark.asyncio
async def test_sort_by_price_asc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=price&sort_order=asc")

    assert response.status_code == 200
    body = response.json()
    
    prices = [Decimal(str(item["price"])) if item["price"] is not None else Decimal(0) for item in body["items"]]
    assert prices == sorted(prices), "Prices should be sorted in ascending order"


@pytest.mark.asyncio
async def test_sort_by_price_desc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=price&sort_order=desc")

    assert response.status_code == 200
    body = response.json()
    
    prices = [Decimal(str(item["price"])) if item["price"] is not None else Decimal(0) for item in body["items"]]
    assert prices == sorted(prices, reverse=True), "Prices should be sorted in descending order"


@pytest.mark.asyncio
async def test_sort_by_date_added_asc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=date_added&sort_order=asc")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0, "Should return products"


@pytest.mark.asyncio
async def test_sort_by_date_added_desc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=date_added&sort_order=desc")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0, "Should return products"


@pytest.mark.asyncio
async def test_sort_by_category_asc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=category&sort_order=asc")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0, "Should return products"
    for item in body["items"]:
        assert len(item["categories"]) >= 1, "Each product should have at least one category"


@pytest.mark.asyncio
async def test_sort_by_category_desc(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=category&sort_order=desc")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0, "Should return products"
    for item in body["items"]:
        assert len(item["categories"]) >= 1, "Each product should have at least one category"


@pytest.mark.asyncio
async def test_sort_with_price_filter(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=name&sort_order=asc&min_price=15&max_price=100")

    assert response.status_code == 200
    body = response.json()
    
    names = [item["name"] for item in body["items"]]
    assert names == sorted(names), "Names should be sorted in ascending order"
    
    for item in body["items"]:
        if item["price"] is not None:
            price = Decimal(str(item["price"]))
            assert price >= Decimal("15")
            assert price <= Decimal("100")


@pytest.mark.asyncio
async def test_sort_with_category_filter(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50&sort_by=price&sort_order=desc&category_id=1")

    assert response.status_code == 200
    body = response.json()
    
    prices = [Decimal(str(item["price"])) if item["price"] is not None else Decimal(0) for item in body["items"]]
    assert prices == sorted(prices, reverse=True), "Prices should be sorted in descending order"
    
    for item in body["items"]:
        assert any(cat for cat in item["categories"])


@pytest.mark.asyncio
async def test_default_sort_without_params(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/product?page=1&size=50")

    assert response.status_code == 200
    body = response.json()
    
    assert len(body["items"]) > 0, "Should return products with default sorting"


@pytest.mark.asyncio
async def test_sort_with_pagination(db_session):
    await cleanup_seed_data(db_session)
    await ensure_demo_data(db_session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response1 = await client.get("/product?page=1&size=2&sort_by=name&sort_order=asc")
        response2 = await client.get("/product?page=2&size=2&sort_by=name&sort_order=asc")

    assert response1.status_code == 200
    assert response2.status_code == 200
    
    body1 = response1.json()
    body2 = response2.json()
    
    names1 = [item["name"] for item in body1["items"]]
    names2 = [item["name"] for item in body2["items"]]
    
    all_names = names1 + names2
    assert all_names == sorted(all_names), "All names across pages should be sorted"
