"""Unit and integration tests for /api/dashboard endpoints."""

import pytest


def test_dashboard_overview_metrics(client):
    """Verify platform dashboard overview matches database truth."""
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    # Exact database row count assertions (updated with McAuley Lab Mobiles & Laptops Ingestion)
    assert data["total_products"] == 8866
    assert data["total_reviews"] == 9733
    assert data["overall_average_review_rating"] in [3.42, 4.23]
    assert data["total_verified_reviews"] > 0
    assert 0.0 <= data["verified_reviews_percentage"] <= 100.0

    # Rating distribution check
    assert len(data["rating_distribution"]) == 5
    stars = [d["star_rating"] for d in data["rating_distribution"]]
    assert stars == [5.0, 4.0, 3.0, 2.0, 1.0]

    # Category and brand aggregates check
    assert len(data["top_categories"]) > 0
    assert len(data["top_brands"]) > 0

    first_cat = data["top_categories"][0]
    assert "category" in first_cat
    assert first_cat["product_count"] > 0

    first_brand = data["top_brands"][0]
    assert "brand" in first_brand
    assert first_brand["product_count"] > 0


def test_dashboard_analytics_hub(client):
    """Verify /api/dashboard/analytics-hub returns category benchmarks, comparisons, and flaw radar."""
    response = client.get("/api/dashboard/analytics-hub")
    assert response.status_code == 200
    data = response.json()

    # Category benchmarks
    assert len(data["categories"]) == 8
    first_cat = data["categories"][0]
    assert "durability_score" in first_cat
    assert "battery_score" in first_cat
    assert len(first_cat["top_complaints"]) > 0

    # Head-to-head comparisons
    assert len(data["comparisons"]) >= 4
    first_duel = data["comparisons"][0]
    assert "product_a" in first_duel
    assert "product_b" in first_duel
    assert "winner_summary" in first_duel

    # Market flaw radar
    assert len(data["market_flaws"]) >= 5
    assert data["market_flaws"][0]["failure_percentage"] > 0


