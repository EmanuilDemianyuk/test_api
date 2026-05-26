import json

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from starlette.requests import Request

from app.core.db import AsyncSessionLocal, engine
from app.core.enums import StatusEnum
from app.main import app, generic_exception_handler, http_exception_handler
from app.models.product import Product


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine_between_tests():
    await engine.dispose()
    yield
    await engine.dispose()


async def make_request() -> Request:
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "http_version": "1.1",
            "root_path": "",
            "app": app,
        },
        receive=receive,
    )


@pytest.mark.asyncio
async def test_validation_errors_return_422():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/product", json={})

    assert response.status_code == 422
    assert response.json()["detail"]


@pytest.mark.asyncio
async def test_missing_category_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/category/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_duplicate_product_returns_409():
    async with AsyncSessionLocal() as session:
        product = Product(
            name="Duplicate seo product",
            description="Duplicate seo product",
            seo_keyword="duplicate-seo-product",
            status=StatusEnum.ENABLED,
            price=10,
            model="DUP-1",
            manufacturer_id=1,
        )
        session.add(product)
        await session.commit()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/product",
                json={
                    "name": "Another duplicate product",
                    "description": "Duplicate product conflict",
                    "seo_keyword": "duplicate-seo-product",
                    "status": StatusEnum.ENABLED.value,
                    "price": "11.00",
                    "model": "DUP-2",
                    "manufacturer_id": 1,
                    "categories": [],
                    "images": [],
                    "attributes": [],
                },
            )

        assert response.status_code == 409
        assert response.json()["detail"] == "Product with this SEO keyword already exists"
    finally:
        async with AsyncSessionLocal() as session:
            existing = await session.scalar(
                select(Product).where(Product.seo_keyword == "duplicate-seo-product")
            )
            if existing is not None:
                await session.delete(existing)
                await session.commit()


@pytest.mark.asyncio
async def test_generic_exception_handler_returns_400():
    request = await make_request()

    response = await generic_exception_handler(request, RuntimeError("boom"))

    assert response.status_code == 400
    assert json.loads(response.body) == {"detail": "Bad request"}


@pytest.mark.asyncio
async def test_http_exception_handler_preserves_status_and_detail():
    request = await make_request()

    response = await http_exception_handler(
        request,
        HTTPException(status_code=404, detail="Category not found"),
    )

    assert response.status_code == 404
    assert json.loads(response.body) == {"detail": "Category not found"}
