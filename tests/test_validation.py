"""Tests for review and product data validation rules."""

import pytest
import pandas as pd
from src.pipeline.validate_data import validate_reviews, validate_products


@pytest.fixture
def sample_valid_data():
    """Synthetic fixture with valid reviews and matching products."""
    products = pd.DataFrame([
        {"product_id": "P001", "product_name": "USB-C Fast Cable", "price": 9.99, "average_rating": 4.5},
        {"product_id": "P002", "product_name": "Wireless Mouse", "price": 19.99, "average_rating": 4.0},
    ])
    reviews = pd.DataFrame([
        {
            "product_id": "P001",
            "review_text": "Works as described.",
            "star_rating": 5.0,
            "helpful_votes": 2,
            "verified_purchase": True,
        },
        {
            "product_id": "P002",
            "review_text": "Good ergonomic feel.",
            "star_rating": 4.0,
            "helpful_votes": 0,
            "verified_purchase": False,
        },
    ])
    return reviews, products


def test_valid_data_passes(sample_valid_data):
    """Verify clean dataset passes all validation checks."""
    reviews, products = sample_valid_data
    rev_val = validate_reviews(reviews, products)
    prod_val = validate_products(products)

    assert rev_val["is_valid"] is True
    assert len(rev_val["violations"]) == 0
    assert prod_val["is_valid"] is True
    assert len(prod_val["violations"]) == 0


def test_invalid_star_ratings_detected(sample_valid_data):
    """Verify out-of-range star ratings (<1.0 or >5.0) are caught."""
    reviews, products = sample_valid_data
    bad_reviews = reviews.copy()
    bad_reviews.loc[0, "star_rating"] = 6.5
    bad_reviews.loc[1, "star_rating"] = -1.0

    val = validate_reviews(bad_reviews, products)
    assert val["is_valid"] is False
    assert val["metrics"]["invalid_star_ratings"] == 2


def test_orphaned_reviews_detected(sample_valid_data):
    """Verify reviews referencing non-existent products trigger validation violation."""
    reviews, products = sample_valid_data
    bad_reviews = reviews.copy()
    bad_reviews.loc[0, "product_id"] = "NON_EXISTENT_ID"

    val = validate_reviews(bad_reviews, products)
    assert val["is_valid"] is False
    assert val["metrics"]["orphaned_reviews"] == 1


def test_negative_prices_detected(sample_valid_data):
    """Verify negative product prices are caught during validation."""
    _, products = sample_valid_data
    bad_products = products.copy()
    bad_products.loc[0, "price"] = -15.99

    val = validate_products(bad_products)
    assert val["is_valid"] is False
    assert val["metrics"]["negative_prices"] == 1

