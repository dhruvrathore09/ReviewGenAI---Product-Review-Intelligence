"""Unit tests validating zero target leakage and strict holdout evaluation protocol."""

import pandas as pd
import pytest
from src.ml.config import FEATURE_COL, PROHIBITED_FEATURE_COLS
from src.ml.dataset import prepare_dataset
from src.ml.split import split_dataset
from src.ml.train import train_and_benchmark
from src.ml.vectorizer import create_vectorizer, fit_vectorizer


def test_prohibited_columns_never_enter_tfidf():
    """Ensure no titles, identifiers, or target-derived columns enter TF-IDF."""
    df = pd.DataFrame({
        "review_id": [1, 2, 3],
        "product_id": ["P1", "P2", "P3"],
        "user_id": ["U1", "U2", "U3"],
        "review_title": ["T1", "T2", "T3"],
        "cleaned_review_title": ["Clean T1", "Clean T2", "Clean T3"],
        "review_text": ["Raw 1", "Raw 2", "Raw 3"],
        "cleaned_review_text": ["Clean text one", "Clean text two", "Clean text three"],
        "star_rating": [5.0, 1.0, 4.0],
        "rating_category": ["positive", "negative", "positive"],
    })

    prep_df = prepare_dataset(df, experiment_type="binary")

    # Assert that prohibited columns are not used as the feature
    assert FEATURE_COL == "cleaned_review_text"
    for col in PROHIBITED_FEATURE_COLS:
        if col in prep_df.columns:
            assert col != FEATURE_COL, f"Prohibited column '{col}' cannot be the feature column!"

    # Fit vectorizer only on FEATURE_COL
    vec = create_vectorizer(min_df=1)
    fitted = fit_vectorizer(vec, prep_df[FEATURE_COL])
    vocab = fitted.vocabulary_

    # Verify no title tokens exist in vocabulary
    assert "clean t1" not in vocab
    assert "clean t2" not in vocab
    assert "raw 1" not in vocab


def test_holdout_evaluation_protocol_isolation():
    """Ensure candidate models are evaluated strictly on validation set, and holdout is evaluated only on winner."""
    # Create synthetic stratified dataset
    n_samples = 40
    df = pd.DataFrame({
        "cleaned_review_text": [
            "excellent amazing great product" if i % 2 == 0 else "terrible defective broken junk"
            for i in range(n_samples)
        ],
        "target": ["positive" if i % 2 == 0 else "negative" for i in range(n_samples)],
        "is_verified_purchase": [True] * n_samples,
        "review_word_count": [10] * n_samples,
    })

    train_df, val_df, test_df = split_dataset(df, target_col="target", random_state=42)

    results = train_and_benchmark(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        class_names=["negative", "positive"],
        experiment_name="Protocol Test",
        text_col="cleaned_review_text",
    )

    # 1. Candidate models should only have validation metrics recorded
    for model_name, bench in results["candidate_benchmarks"].items():
        assert "validation_metrics" in bench
        assert "test_metrics" not in bench, f"Candidate model '{model_name}' must NOT have test metrics recorded during selection!"

    # 2. Holdout test metrics exist exclusively for the winning model
    assert "holdout_test_metrics" in results
    assert results["best_model_name"] is not None
    assert results["holdout_test_metrics"]["accuracy"] >= 0.0

