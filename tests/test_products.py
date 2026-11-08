"""Unit and integration tests for /api/products endpoints."""

import pytest


def test_list_products_default(client):
    """Verify default product listing returns 20 items and correct pagination metadata."""
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 8866
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 20
    assert data["total_pages"] == 444

    # Check structure of first item
    first_item = data["items"][0]
    assert "product_id" in first_item
    assert "product_name" in first_item
    assert "db_review_count" in first_item


def test_list_products_pagination(client):
    """Verify custom page and page_size parameters."""
    response = client.get("/api/products?page=3&page_size=15")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 3
    assert data["page_size"] == 15
    assert len(data["items"]) == 15


def test_list_products_invalid_rating_range(client):
    """Verify 400 Bad Request when min_rating > max_rating."""
    response = client.get("/api/products?min_rating=4.5&max_rating=2.0")
    assert response.status_code == 400
    assert "min_rating cannot be greater than max_rating" in response.json()["detail"]


def test_list_products_brand_filter(client):
    """Verify brand filtering returns only products for that brand."""
    response = client.get("/api/products?brand=Amazon")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["brand"].lower() == "amazon"


def test_search_products_success(client):
    """Verify product search returns relevant results."""
    response = client.get("/api/products/search?q=Cable")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0


def test_search_products_missing_query(client):
    """Verify 422 Unprocessable Entity when search query q is missing."""
    response = client.get("/api/products/search")
    assert response.status_code == 422


def test_get_product_detail_success(client):
    """Verify retrieving details for an existing product."""
    response = client.get("/api/products/B075X8471B")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "B075X8471B"
    assert "Fire TV Stick" in data["product_name"]
    assert data["brand"] == "Amazon"
    assert "categories_hierarchy" in data
    assert data["db_review_count"] >= 1


def test_get_product_detail_not_found(client):
    """Verify 404 response for non-existent product ASIN."""
    response = client.get("/api/products/INVALID_ASIN_99999")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_get_product_statistics_success(client):
    """Verify calculated rating statistics for an existing product."""
    response = client.get("/api/products/B075X8471B/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "B075X8471B"
    assert data["total_reviews"] >= 1
    assert data["average_review_rating"] is not None
    assert len(data["star_distribution"]) == 5
    assert data["verified_purchases_percentage"] >= 0.0


def test_get_product_statistics_not_found(client):
    """Verify 404 response for statistics of non-existent product."""
    response = client.get("/api/products/NON_EXISTENT_PRODUCT/statistics")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_route_ordering_search_not_intercepted_by_product_id(client):
    """Verify that /api/products/search is not intercepted by /api/products/{product_id}."""
    # When query is provided, it must hit the search handler (200), not product detail 404
    response = client.get("/api/products/search?q=Amazon")
    assert response.status_code == 200
    assert "items" in response.json()

    # When query is missing, it must return 422 validation error, not 404
    response_no_q = client.get("/api/products/search")
    assert response_no_q.status_code == 422


def test_list_products_category_scoping(client):
    """Verify category filtering strictly scopes products to the specified category."""
    response = client.get("/api/products?category=Computers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["main_category"].lower() == "computers"


def test_list_products_headphones_section_strict_scoping(client):
    """Verify headphones section returns genuine headphones and zero cables/cases."""
    response = client.get("/api/products?category=Headphones%20%26%20Earbuds")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    non_headphone_keywords = ["cable", "adapter", "backpack", "carrying case", "case cover"]
    for item in data["items"]:
        title_lower = item["product_name"].lower()
        for kw in non_headphone_keywords:
            assert kw not in title_lower, f"Unexpected non-headphone item found in headphones: {item['product_name']}"


def test_search_scoped_within_category(client):
    """Verify search within category only returns items matching both category and search query."""
    response = client.get("/api/products?category=Headphones%20%26%20Earbuds&q=Sony")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        # Must match Sony in brand or title
        assert "sony" in item["product_name"].lower() or (item["brand"] and "sony" in item["brand"].lower())
        # Must not be a cable or case
        assert "cable" not in item["product_name"].lower()
        assert "case" not in item["product_name"].lower()


def test_list_products_laptops_section_strict_scoping(client):
    """Verify laptops section returns genuine laptops and zero accessories."""
    response = client.get("/api/products?category=Laptops%20%26%20Notebooks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1600
    non_laptop_keywords = ["backpack", "carrying case", "charger cable", "cooling pad", "docking station"]
    for item in data["items"]:
        title_lower = item["product_name"].lower()
        for kw in non_laptop_keywords:
            assert kw not in title_lower, f"Unexpected accessory found in laptops: {item['product_name']}"


def test_list_products_cameras_section_strict_scoping(client):
    """Verify cameras section returns genuine cameras/lenses and zero accessories."""
    response = client.get("/api/products?category=Cameras%20%26%20Photography")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 300
    non_camera_keywords = ["camera bag", "tripod stand", "battery charger", "cleaning cloth"]
    for item in data["items"]:
        title_lower = item["product_name"].lower()
        for kw in non_camera_keywords:
            assert kw not in title_lower, f"Unexpected accessory found in cameras: {item['product_name']}"


def test_list_products_hard_disks_section_strict_scoping(client):
    """Verify hard disks section returns genuine storage drives/SSDs and zero accessories."""
    response = client.get("/api/products?category=Hard%20Disks%20%26%20Storage")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 400
    non_storage_keywords = ["carrying case", "hard drive enclosure", "docking station", "caddy"]
    for item in data["items"]:
        title_lower = item["product_name"].lower()
        for kw in non_storage_keywords:
            assert kw not in title_lower, f"Unexpected accessory found in hard disks: {item['product_name']}"


def test_smart_search_category_resolution_laptop(client: TestClient):
    """Verify querying q='laptop' automatically scopes to genuine laptops without sleeves or mice."""
    response = client.get("/api/products?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1000
    for item in data["items"]:
        title_lower = item["product_name"].lower()
        for kw in ["sleeve", "backpack", "cooling pad"]:
            assert kw not in title_lower, f"Found non-laptop accessory in laptop search: {item['product_name']}"


def test_smart_search_brand_and_category_hp_laptop(client: TestClient):
    """Verify querying q='HP laptop' scopes to genuine HP laptops."""
    response = client.get("/api/products?q=HP%20laptop")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 200
    for item in data["items"]:
        assert "hp" in item["brand"].lower() or "hp" in item["product_name"].lower()
        title_lower = item["product_name"].lower()
        for kw in ["sleeve", "backpack"]:
            assert kw not in title_lower, f"Found accessory in HP laptop search: {item['product_name']}"


def test_get_product_intelligence_report_success(client: TestClient):
    """Verify that /api/products/{product_id}/report returns full intelligence report with durability and lifespan."""
    response = client.get("/api/products/B075X8471B/report")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "B075X8471B"
    assert data["overall_rating"] > 0
    assert data["quality_grade"] in ["A+", "A", "B+", "B", "C"]
    assert len(data["aspects"]) == 5
    aspect_names = [a["name"] for a in data["aspects"]]
    assert any("durability" in a.lower() for a in aspect_names)
    assert any("lifespan" in a.lower() or "battery" in a.lower() for a in aspect_names)
    assert len(data["strengths"]) > 0
    assert len(data["flaws_and_drawbacks"]) > 0
    assert len(data["durability_and_longevity_deep_dive"]) > 20
    assert data["who_should_buy"] is not None
    assert data["who_should_skip"] is not None


def test_get_product_intelligence_report_not_found(client: TestClient):
    """Verify 404 response for intelligence report of non-existent product."""
    response = client.get("/api/products/NON_EXISTENT_PRODUCT/report")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]






