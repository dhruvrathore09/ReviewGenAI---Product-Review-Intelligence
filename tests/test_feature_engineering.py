"""Tests for feature engineering, temporal extractions, and weak-supervision sentiment labeling."""

import pytest
import pandas as pd
from src.pipeline.feature_engineering import engineer_review_features, map_rating_to_category


def test_rating_category_mapping():
    """Verify weak-supervision proxy rules across 1 to 5 star ratings."""
    assert map_rating_to_category(5.0) == "positive"
    assert map_rating_to_category(4.0) == "positive"
    assert map_rating_to_category(3.0) == "neutral"
    assert map_rating_to_category(2.0) == "negative"
    assert map_rating_to_category(1.0) == "negative"


def test_feature_engineering_calculations():
    """Verify lexical length, date extractions, and boolean flags."""
    df = pd.DataFrame([
        {
            "review_title": "Super Fast Charger",
            "review_text": "Charges my phone from 0 to 80% in 30 minutes! Highly recommend.",
            "cleaned_review_text": "Charges my phone from 0 to 80% in 30 minutes! Highly recommend.",
            "star_rating": 5.0,
            "review_date": "2021-07-15 14:30:00",
            "verified_purchase": True,
        },
        {
            "review_title": "Broke immediately",
            "review_text": "Stopped working.",
            "cleaned_review_text": "Stopped working.",
            "star_rating": 1.0,
            "review_date": "2022-11-03 09:12:00",
            "verified_purchase": "False",
        },
    ])

    res = engineer_review_features(df)

    # 1. Lexical features
    assert res.loc[0, "title_length"] == len("Super Fast Charger")
    assert res.loc[0, "review_word_count"] == 12
    assert res.loc[0, "review_text_length"] == len("Charges my phone from 0 to 80% in 30 minutes! Highly recommend.")

    # 2. Temporal features
    assert res.loc[0, "review_year"] == 2021
    assert res.loc[0, "review_month"] == 7
    assert res.loc[0, "review_quarter"] == 3

    assert res.loc[1, "review_year"] == 2022
    assert res.loc[1, "review_month"] == 11
    assert res.loc[1, "review_quarter"] == 4

    # 3. Verified boolean
    assert bool(res.loc[0, "is_verified_purchase"]) is True
    assert bool(res.loc[1, "is_verified_purchase"]) is False

    # 4. Proxy sentiment category
    assert res.loc[0, "rating_category"] == "positive"
    assert res.loc[1, "rating_category"] == "negative"
