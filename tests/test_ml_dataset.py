"""Unit tests for ML dataset preparation enforcing strict feature and target contracts."""

import pandas as pd
import pytest
from src.ml.config import FEATURE_COL
from src.ml.dataset import prepare_dataset


def test_prepare_dataset_strictly_uses_cleaned_review_text():
    # Synthetic dataframe with titles and body
    df = pd.DataFrame({
        "cleaned_review_title": ["MISLEADING TITLE THAT SHOULD NEVER BE USED"],
        "cleaned_review_text": ["This is the genuine customer feedback."],
        "star_rating": [5.0],
    })

    prep_df = prepare_dataset(df, experiment_type="binary")
    
    # Assert primary feature is cleaned_review_text
    assert FEATURE_COL in prep_df.columns
    # Assert title text is NOT concatenated into the feature text
    assert "MISLEADING TITLE" not in prep_df[FEATURE_COL].iloc[0]
    assert prep_df[FEATURE_COL].iloc[0] == "This is the genuine customer feedback."


def test_prepare_dataset_binary_filtering():
    df = pd.DataFrame({
        "cleaned_review_title": ["Good", "Average", "Terrible"],
        "cleaned_review_text": ["Love it", "It is okay", "Broke instantly"],
        "star_rating": [5.0, 3.0, 1.0],
    })

    binary_df = prepare_dataset(df, experiment_type="binary")
    # 3.0 stars must be excluded
    assert len(binary_df) == 2
    assert "neutral" not in binary_df["target"].values
    assert set(binary_df["target"].unique()) == {"positive", "negative"}


def test_prepare_dataset_three_class():
    df = pd.DataFrame({
        "cleaned_review_title": ["Good", "Average", "Terrible"],
        "cleaned_review_text": ["Love it", "It is okay", "Broke instantly"],
        "star_rating": [5.0, 3.0, 1.0],
    })

    three_df = prepare_dataset(df, experiment_type="three_class")
    assert len(three_df) == 3
    assert set(three_df["target"].unique()) == {"positive", "neutral", "negative"}


def test_prepare_dataset_drops_empty_cleaned_text():
    df = pd.DataFrame({
        "cleaned_review_text": ["   ", "Valid review text", ""],
        "star_rating": [5.0, 4.0, 1.0],
    })
    prep_df = prepare_dataset(df, experiment_type="binary")
    assert len(prep_df) == 1
    assert prep_df[FEATURE_COL].iloc[0] == "Valid review text"
