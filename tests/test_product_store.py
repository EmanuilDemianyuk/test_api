import pytest

from tests.seeders import create_product, create_store


@pytest.mark.asyncio
async def test_get_product_stores_returns_store_list(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Store product",
        seo_keyword="store-product",
    )

    store_id = await create_store(
        session=db_session,
        name="Main Store",
    )

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 201

    response = await client.get(
        f"/product/{product_id}/store",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["store_id"] == store_id
    assert data[0]["name"] == "Main Store"


@pytest.mark.asyncio
async def test_get_product_stores_returns_404_for_invalid_product(
    client,
):
    response = await client.get(
        "/product/999999/store",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_add_store_to_product_success(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Attach store product",
        seo_keyword="attach-store-product",
    )

    store_id = await create_store(
        session=db_session,
        name="Attached Store",
    )

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Store added to product"

    response = await client.get(
        f"/product/{product_id}/store",
    )

    data = response.json()

    assert len(data) == 1
    assert data[0]["store_id"] == store_id


@pytest.mark.asyncio
async def test_add_store_to_product_returns_404_for_invalid_product(
    client,
    db_session,
):
    store_id = await create_store(
        session=db_session,
        name="Store",
    )

    response = await client.post(
        "/product/999999/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_add_store_to_product_returns_404_for_invalid_store(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Invalid store product",
        seo_keyword="invalid-store-product",
    )

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found"


@pytest.mark.asyncio
async def test_add_store_to_product_returns_409_for_duplicate_relation(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Duplicate relation product",
        seo_keyword="duplicate-relation-product",
    )

    store_id = await create_store(
        session=db_session,
        name="Duplicate Store",
    )

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 201

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Store already attached to product"
    )


@pytest.mark.asyncio
async def test_delete_store_from_product_success(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Delete store product",
        seo_keyword="delete-store-product",
    )

    store_id = await create_store(
        session=db_session,
        name="Delete Store",
    )

    response = await client.post(
        f"/product/{product_id}/store",
        json={
            "store_id": store_id,
        },
    )

    assert response.status_code == 201

    response = await client.delete(
        f"/product/{product_id}/store/{store_id}",
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Store removed from product"

    response = await client.get(
        f"/product/{product_id}/store",
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_delete_store_from_product_returns_404_for_invalid_product(
    client,
):
    response = await client.delete(
        "/product/999999/store/1",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_delete_store_from_product_returns_404_for_missing_relation(
    client,
    db_session,
):
    product_id = await create_product(
        session=db_session,
        name="Missing relation product",
        seo_keyword="missing-relation-product",
    )

    store_id = await create_store(
        session=db_session,
        name="Missing Relation Store",
    )

    response = await client.delete(
        f"/product/{product_id}/store/{store_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store relation not found"