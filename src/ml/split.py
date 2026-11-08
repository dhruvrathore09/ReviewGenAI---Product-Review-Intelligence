"""Stratified train/validation/test dataset splitting module enforcing strict featurization ordering."""

import logging
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.ml.config import SPLIT_RANDOM_STATE, TEST_RATIO, TRAIN_RATIO, VAL_RATIO

logger = logging.getLogger(__name__)


def split_dataset(
    df: pd.DataFrame,
    target_col: str = "target",
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    random_state: int = SPLIT_RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split dataset into stratified Train, Validation, and Test sets.
    
    Strict Featurization Ordering (ml-best-practices):
    Dataset splitting must ALWAYS occur BEFORE fitting vectorizers, scalers, or encoders
    to guarantee zero data leakage between training and evaluation splits.
    
    Args:
        df: Input DataFrame.
        target_col: Target column name for stratified distribution.
        train_ratio: Proportion of data for training (default 0.70).
        val_ratio: Proportion of data for validation (default 0.15).
        test_ratio: Proportion of data for final testing (default 0.15).
        random_state: Reproducibility seed.
        
    Returns:
        Tuple of (train_df, val_df, test_df) as independent DataFrames.
    """
    total_ratio = train_ratio + val_ratio + test_ratio
    if not np.isclose(total_ratio, 1.0):
        raise ValueError(f"Split ratios must sum to 1.0, got {total_ratio:.4f}")

    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in DataFrame.")

    # Stage 1: Split into Train (70%) and Temp (30%)
    temp_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_ratio,
        stratify=df[target_col],
        random_state=random_state,
    )

    # Stage 2: Split Temp into Validation (15%) and Test (15%)
    # relative proportion: 0.15 / 0.30 = 0.50
    relative_test_ratio = test_ratio / temp_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_ratio,
        stratify=temp_df[target_col],
        random_state=random_state,
    )

    # Reset indices for clean downstream indexing
    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    logger.info(
        "Stratified Split Completed: Train=%d (%.1f%%) | Val=%d (%.1f%%) | Test=%d (%.1f%%)",
        len(train_df),
        (len(train_df) / len(df)) * 100,
        len(val_df),
        (len(val_df) / len(df)) * 100,
        len(test_df),
        (len(test_df) / len(df)) * 100,
    )

    return train_df, val_df, test_df

