"""Unit tests for TF-IDF vectorization and serialization."""

import pytest
from src.ml.vectorizer import create_vectorizer, fit_vectorizer, load_vectorizer, save_vectorizer, transform_texts


def test_vectorizer_ngram_and_transformation(tmp_path):
    texts = [
        "This product is not working properly",
        "Great quality battery and fast charging",
        "Worst customer service ever",
    ]
    vec = create_vectorizer(ngram_range=(1, 2), min_df=1)
    fitted = fit_vectorizer(vec, texts)

    # Test bigram capture (e.g. 'not working')
    vocab = fitted.vocabulary_
    assert "not working" in vocab or "fast charging" in vocab

    # Transform
    matrix = transform_texts(fitted, ["This product is fast charging"])
    assert matrix.shape[0] == 1
    assert matrix.shape[1] == len(vocab)

    # Persistence
    save_file = tmp_path / "vec.joblib"
    save_vectorizer(fitted, save_file)
    loaded = load_vectorizer(save_file)
    assert len(loaded.vocabulary_) == len(vocab)

