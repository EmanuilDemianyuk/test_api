import pytest


@pytest.mark.asyncio
async def test_create_product_image(
    client,
):
    product_response = await client.post(
        "/product",
        json={
            "name": "iPhone 15",
        },
    )

    assert product_response.status_code == 201

    product_id = (
        product_response.json()["product_id"]
    )

    image_response = await client.post(
        f"/product/{product_id}/image",
        json={
            "image": "iphone.jpg",
            "sort_order": 1,
        },
    )

    assert image_response.status_code == 201

    image_data = image_response.json()

    assert (
        image_data["product_id"]
        == product_id
    )

    assert (
        image_data["image"]
        == "iphone.jpg"
    )

    assert (
        image_data["sort_order"]
        == 1
    )

    assert (
        "product_image_id"
        in image_data
    )


@pytest.mark.asyncio
async def test_get_product_images(
    client,
):
    product_response = await client.post(
        "/product",
        json={
            "name": "MacBook Pro",
        },
    )

    assert product_response.status_code == 201

    product_id = (
        product_response.json()["product_id"]
    )

    response_1 = await client.post(
        f"/product/{product_id}/image",
        json={
            "image": "macbook-1.jpg",
            "sort_order": 1,
        },
    )

    assert response_1.status_code == 201

    response_2 = await client.post(
        f"/product/{product_id}/image",
        json={
            "image": "macbook-2.jpg",
            "sort_order": 2,
        },
    )

    assert response_2.status_code == 201

    response = await client.get(
        f"/product/{product_id}/image"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert (
        data[0]["image"]
        == "macbook-1.jpg"
    )

    assert (
        data[1]["image"]
        == "macbook-2.jpg"
    )


@pytest.mark.asyncio
async def test_delete_product_image(
    client,
):
    product_response = await client.post(
        "/product",
        json={
            "name": "PlayStation 5",
        },
    )

    assert product_response.status_code == 201

    product_id = (
        product_response.json()["product_id"]
    )

    image_response = await client.post(
        f"/product/{product_id}/image",
        json={
            "image": "ps5.jpg",
            "sort_order": 1,
        },
    )

    assert image_response.status_code == 201

    image_id = (
        image_response.json()[
            "product_image_id"
        ]
    )

    delete_response = await client.delete(
        f"/product/{product_id}/image/{image_id}"
    )

    assert delete_response.status_code == 204

    images_response = await client.get(
        f"/product/{product_id}/image"
    )

    assert images_response.status_code == 200

    images = images_response.json()

    assert len(images) == 0


@pytest.mark.asyncio
async def test_create_product_image_for_invalid_product(
    client,
):
    response = await client.post(
        "/product/999999/image",
        json={
            "image": "invalid.jpg",
            "sort_order": 1,
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Product not found"
    )


@pytest.mark.asyncio
async def test_delete_nonexistent_product_image(
    client,
):
    product_response = await client.post(
        "/product",
        json={
            "name": "Nintendo Switch",
        },
    )

    assert product_response.status_code == 201

    product_id = (
        product_response.json()["product_id"]
    )

    response = await client.delete(
        f"/product/{product_id}/image/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Image not found"
    )