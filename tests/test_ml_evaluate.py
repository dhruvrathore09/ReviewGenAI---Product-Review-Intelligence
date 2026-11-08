"""Unit tests for ML evaluation metrics and confusion matrix calculations."""

import pytest
from src.ml.evaluate import evaluate_predictions


def test_evaluate_predictions_metrics():
    y_true = ["positive", "positive", "negative", "negative"]
    y_pred = ["positive", "negative", "negative", "positive"]
    class_names = ["negative", "positive"]

    metrics = evaluate_predictions(y_true, y_pred, class_names)

    # 2 out of 4 correct -> accuracy 0.5
    assert metrics["accuracy"] == 0.5
    assert "macro_f1" in metrics
    assert "weighted_f1" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert "negative" in metrics["per_class"]
    assert "positive" in metrics["per_class"]

