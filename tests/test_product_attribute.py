import pytest


@pytest.mark.asyncio
async def test_create_product_attribute(client):
    product_response = await client.post(
        "/product",
        json={
            "name": "Phone",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    response = await client.post(
        f"/product/{product_id}/attribute",
        json={
            "group_name": "Specs",
            "name": "Color",
            "value": "Black",
            "sort_order": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product_attribute_id"]
    assert data["group_name"] == "Specs"
    assert data["name"] == "Color"
    assert data["value"] == "Black"
    assert data["sort_order"] == 2


@pytest.mark.asyncio
async def test_get_product_attributes(client):
    product_response = await client.post(
        "/product",
        json={
            "name": "Laptop",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    await client.post(
        f"/product/{product_id}/attribute",
        json={
            "name": "Memory",
            "value": "16GB",
            "sort_order": 1,
        },
    )

    await client.post(
        f"/product/{product_id}/attribute",
        json={
            "group_name": "Warranty",
            "name": "Period",
            "value": "12 months",
            "sort_order": 2,
        },
    )

    response = await client.get(f"/product/{product_id}/attribute")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Memory"
    assert data[1]["name"] == "Period"


@pytest.mark.asyncio
async def test_patch_product_attribute(client):
    product_response = await client.post(
        "/product",
        json={
            "name": "Tablet",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    created = await client.post(
        f"/product/{product_id}/attribute",
        json={
            "group_name": "General",
            "name": "Storage",
            "value": "64GB",
            "sort_order": 1,
        },
    )

    assert created.status_code == 201

    attribute_id = created.json()["product_attribute_id"]

    response = await client.patch(
        f"/product/{product_id}/attribute/{attribute_id}",
        json={
            "name": "Storage capacity",
            "value": "128GB",
            "sort_order": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Storage capacity"
    assert data["value"] == "128GB"
    assert data["sort_order"] == 3
    assert data["group_name"] == "General"


@pytest.mark.asyncio
async def test_delete_product_attribute(client):
    product_response = await client.post(
        "/product",
        json={
            "name": "Camera",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    created = await client.post(
        f"/product/{product_id}/attribute",
        json={
            "name": "Lens",
            "value": "50mm",
        },
    )

    assert created.status_code == 201

    attribute_id = created.json()["product_attribute_id"]

    delete_response = await client.delete(
        f"/product/{product_id}/attribute/{attribute_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(f"/product/{product_id}/attribute")

    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.asyncio
async def test_product_attribute_not_found(client):
    product_response = await client.post(
        "/product",
        json={
            "name": "Monitor",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["product_id"]

    response = await client.patch(
        f"/product/{product_id}/attribute/999999",
        json={
            "name": "Unknown",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attribute not found"
