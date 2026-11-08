"""Unit tests for ML sentiment inference and persistence."""

import pytest
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from src.ml.persistence import save_experiment_artifacts
from src.ml.predictor import SentimentPredictor


def test_sentiment_predictor_inference(tmp_path):
    # Create simple dummy model and vectorizer
    vec = TfidfVectorizer()
    X = vec.fit_transform(["great product", "terrible junk"])
    clf = DummyClassifier(strategy="most_frequent")
    clf.fit(X, ["positive", "negative"])

    metrics_mock = {
        "test_metrics": {
            "confusion_matrix": [[1, 0], [0, 1]],
            "accuracy": 1.0,
            "macro_f1": 1.0,
        }
    }

    art_dict = save_experiment_artifacts(
        output_dir=tmp_path,
        model=clf,
        vectorizer=vec,
        metrics=metrics_mock,
        class_names=["negative", "positive"],
        experiment_title="Test Experiment",
    )

    predictor = SentimentPredictor(artifact_dir=tmp_path)
    res = predictor.predict("great product")

    assert "label" in res
    assert "confidence" in res
    assert "probabilities" in res
    assert res["is_empty"] is False

    # Empty text test
    empty_res = predictor.predict("   ")
    assert empty_res["is_empty"] is True

