"""Tests for duplicate detection distinguishing exact vs contextual duplicates."""

import pytest
import pandas as pd
from src.pipeline.duplicate_detection import detect_review_duplicates, detect_product_duplicates


def test_no_duplicates_in_clean_data():
    """Verify clean dataset returns 0 duplicates across all levels."""
    reviews = pd.DataFrame([
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Great"},
        {"product_id": "P1", "user_id": "U2", "review_timestamp": 2000, "cleaned_review_text": "Not bad"},
    ])
    res = detect_review_duplicates(reviews)
    assert res["exact_duplicates"]["count"] == 0
    assert res["event_key_duplicates"]["count"] == 0


def test_exact_duplicates_detected():
    """Verify identical duplicate rows are detected."""
    reviews = pd.DataFrame([
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Great"},
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Great"},
    ])
    res = detect_review_duplicates(reviews)
    assert res["exact_duplicates"]["count"] == 2


def test_event_key_duplicates_detected():
    """Verify same user reviewing same product at same timestamp is flagged."""
    reviews = pd.DataFrame([
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Review A"},
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Review B"},
    ])
    res = detect_review_duplicates(reviews)
    assert res["event_key_duplicates"]["count"] == 2


def test_content_duplicate_not_flagged_as_exact():
    """Verify identical text from different users is categorized as content duplicate, not exact."""
    reviews = pd.DataFrame([
        {"product_id": "P1", "user_id": "U1", "review_timestamp": 1000, "cleaned_review_text": "Works great!"},
        {"product_id": "P1", "user_id": "U2", "review_timestamp": 2000, "cleaned_review_text": "Works great!"},
    ])
    res = detect_review_duplicates(reviews)
    assert res["exact_duplicates"]["count"] == 0
    assert res["event_key_duplicates"]["count"] == 0
    assert res["content_duplicates"]["count"] == 2

