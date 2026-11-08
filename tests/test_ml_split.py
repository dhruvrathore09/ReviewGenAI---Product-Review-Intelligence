"""Unit tests for ML stratified train/validation/test splitting."""

import numpy as np
import pandas as pd
import pytest
from src.ml.split import split_dataset


def test_split_dataset_proportions_and_stratification():
    # Synthetic dataset with imbalanced classes: 80% positive, 20% negative
    n_samples = 1000
    targets = ["positive"] * 800 + ["negative"] * 200
    df = pd.DataFrame({
        "full_text": [f"Review text sample {i}" for i in range(n_samples)],
        "target": targets,
    })

    train_df, val_df, test_df = split_dataset(df, target_col="target", random_state=42)

    # 70% train (700), 15% val (150), 15% test (150)
    assert len(train_df) == 700
    assert len(val_df) == 150
    assert len(test_df) == 150

    # Verify class proportions across splits (approx 80% positive, 20% negative)
    for split_df in [train_df, val_df, test_df]:
        pos_ratio = (split_df["target"] == "positive").mean()
        assert np.isclose(pos_ratio, 0.80, atol=0.02)


def test_split_dataset_invalid_ratios():
    df = pd.DataFrame({"full_text": ["a", "b"], "target": ["pos", "neg"]})
    with pytest.raises(ValueError, match="Split ratios must sum to 1.0"):
        split_dataset(df, train_ratio=0.5, val_ratio=0.2, test_ratio=0.2)

