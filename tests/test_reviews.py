"""Unit and integration tests for /api/products/{product_id}/reviews endpoints."""

import pytest


def test_get_product_reviews_success(client):
    """Verify fetching paginated reviews for a valid product."""
    response = client.get("/api/products/B075X8471B/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["page"] == 1
    assert len(data["items"]) >= 1

    first_review = data["items"][0]
    assert "review_id" in first_review
    assert "review_text" in first_review
    assert "star_rating" in first_review
    assert "review_date" in first_review
    assert "verified_purchase" in first_review


def test_get_product_reviews_not_found(client):
    """Verify 404 response when querying reviews for a non-existent product."""
    response = client.get("/api/products/NON_EXISTENT_PRODUCT/reviews")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_get_product_reviews_filter_star(client):
    """Verify filtering reviews by exact star rating."""
    response = client.get("/api/products/B075X8471B/reviews?star_rating=4.0")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["star_rating"] == 4.0


def test_get_product_reviews_filter_verified(client):
    """Verify filtering reviews by verified purchase."""
    response = client.get("/api/products/B075X8471B/reviews?verified_only=true")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["verified_purchase"] is True


def test_get_product_reviews_sorting(client):
    """Verify sorting reviews by date ascending."""
    response = client.get("/api/products/B075X8471B/reviews?sort_by=date&order=asc")
    assert response.status_code == 200
    data = response.json()
    if len(data["items"]) > 1:
        dates = [item["review_date"] for item in data["items"]]
        assert dates == sorted(dates)

