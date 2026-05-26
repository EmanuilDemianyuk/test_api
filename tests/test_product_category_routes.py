import pytest

from app.core.enums import StatusEnum
from app.models.category import Category


@pytest.mark.asyncio
async def test_create_product_category(client, db_session):
    product_response = await client.post(
        "/product",
        json={
            "name": "Category-bound product",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    category = Category(
        name="Accessories",
        status=StatusEnum.ENABLED,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    response = await client.post(
        f"/product/{product_id}/category",
        json={
            "category_id": category.category_id,
        },
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["category_id"] == category.category_id
    assert payload["category_name"] == "Accessories"
    assert payload["full_path"] == "Accessories"
    assert "product_category_id" in payload


@pytest.mark.asyncio
async def test_get_product_categories(client, db_session):
    product_response = await client.post(
        "/product",
        json={
            "name": "Product with categories",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    category = Category(
        name="Electronics",
        status=StatusEnum.ENABLED,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    attach_response = await client.post(
        f"/product/{product_id}/category",
        json={
            "category_id": category.category_id,
        },
    )

    assert attach_response.status_code == 201

    response = await client.get(
        f"/product/{product_id}/category"
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["category_id"] == category.category_id
    assert payload[0]["category_name"] == "Electronics"
    assert payload[0]["full_path"] == "Electronics"


@pytest.mark.asyncio
async def test_delete_product_category(client, db_session):
    product_response = await client.post(
        "/product",
        json={
            "name": "Delete category product",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    category = Category(
        name="Kitchen",
        status=StatusEnum.ENABLED,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    attach_response = await client.post(
        f"/product/{product_id}/category",
        json={
            "category_id": category.category_id,
        },
    )

    assert attach_response.status_code == 201

    category_id = attach_response.json()["category_id"]

    delete_response = await client.delete(
        f"/product/{product_id}/category/{category_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/product/{product_id}/category"
    )

    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.asyncio
async def test_product_category_routes_return_404_for_missing_product(client):
    response = await client.get("/product/999999/category")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

    create_response = await client.post(
        "/product/999999/category",
        json={
            "category_id": 1,
        },
    )

    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "Product not found"

    delete_response = await client.delete(
        "/product/999999/category/1"
    )

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Product not found"
