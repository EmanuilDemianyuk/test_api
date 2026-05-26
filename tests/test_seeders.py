import pytest


@pytest.mark.asyncio
async def test_seeded_test_data_fixture_creates_related_entities(seeded_test_data):
    assert seeded_test_data.category_tree.root_category.category_id is not None
    assert seeded_test_data.category_tree.child_category.parent_category_id == (
        seeded_test_data.category_tree.root_category.category_id
    )

    assert seeded_test_data.product.product.name.startswith("Seed Product-")
    assert seeded_test_data.product.product_category.category_id == (
        seeded_test_data.category_tree.child_category.category_id
    )
    assert seeded_test_data.product.product_image.sort_order == 0
    assert seeded_test_data.product.product_attribute.name == "Size"
