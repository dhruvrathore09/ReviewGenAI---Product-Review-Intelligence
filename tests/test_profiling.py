"""Tests for dataset profiling and quality report generation."""

import pytest
import pandas as pd
from src.pipeline.profiling import profile_reviews, profile_products, format_profiling_markdown


def test_profiling_computations():
    """Verify profiling metrics accurately summarize review distributions."""
    reviews = pd.DataFrame([
        {"review_text": "Short", "star_rating": 5.0, "verified_purchase": True, "review_date": "2020-01-01"},
        {"review_text": "A longer review text here", "star_rating": 1.0, "verified_purchase": False, "review_date": "2022-01-01"},
    ])
    products = pd.DataFrame([
        {"product_id": "P1", "product_name": "Product 1", "price": 10.0, "brand": "BrandA", "main_category": "Electronics", "average_rating": 4.0},
        {"product_id": "P2", "product_name": "Product 2", "price": None, "brand": "Unknown", "main_category": "Electronics", "average_rating": 3.0},
    ])

    rev_profile = profile_reviews(reviews)
    prod_profile = profile_products(products)

    # Reviews profile assertions
    assert rev_profile["total_reviews"] == 2
    assert rev_profile["star_rating_distribution"]["5.0"]["count"] == 1
    assert rev_profile["star_rating_distribution"]["1.0"]["count"] == 1
    assert rev_profile["verified_purchase"]["verified_count"] == 1
    assert rev_profile["verified_purchase"]["non_verified_count"] == 1

    # Products profile assertions
    assert prod_profile["total_products"] == 2
    assert prod_profile["missing_prices"] == 1
    assert prod_profile["missing_or_unknown_brands"] == 1

    # Markdown format check
    md = format_profiling_markdown(rev_profile, prod_profile)
    assert "# Data Profiling & Quality Audit Report" in md
    assert "Verified Purchases" in md

