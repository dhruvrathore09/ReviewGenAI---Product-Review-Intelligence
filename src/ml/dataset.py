"""Dataset loading and preparation module enforcing strict Level 5 feature contracts."""

import logging
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

from src.ml.config import (
    BINARY_CLASSES,
    FEATURE_COL,
    NEGATIVE_RATING_MAX,
    NEUTRAL_RATING_VAL,
    POSITIVE_RATING_MIN,
    PROCESSED_REVIEWS_PATH,
    PROHIBITED_FEATURE_COLS,
    THREE_CLASSES,
)

logger = logging.getLogger(__name__)


def load_processed_reviews(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the Level 4 processed reviews dataset without modification."""
    path = Path(csv_path or PROCESSED_REVIEWS_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"Processed reviews dataset not found at '{path}'. "
            "Please run the Level 4 data pipeline first: python -m src.pipeline.run_pipeline"
        )
    logger.info("Loading processed reviews dataset from %s...", path)
    df = pd.read_csv(path, keep_default_na=False)
    logger.info("Loaded %d review records from Level 4 output.", len(df))
    return df


def prepare_dataset(
    df: pd.DataFrame,
    experiment_type: str = "binary",
) -> pd.DataFrame:
    """Prepare labeled review dataset strictly complying with the Level 5 Feature Contract.
    
    Feature & Target Contracts:
    1. Primary Model Input: `cleaned_review_text` STRICTLY.
    2. Prohibited Features: Review titles (`cleaned_review_title`), IDs, numerical metadata,
       and rating-derived columns are NEVER concatenated or used as TF-IDF input.
    3. Target Label Source: Derived exclusively from `star_rating`.
    
    Args:
        df: Input DataFrame from reviews_processed.csv.
        experiment_type: Either 'binary' (excludes 3-star reviews) or 'three_class' (all reviews).
        
    Returns:
        Prepared DataFrame with `cleaned_review_text`, `target`, and non-leaking slice metadata.
    """
    logger.info("Preparing dataset for experiment: '%s'...", experiment_type)
    data = df.copy()

    # 1. Enforce Primary Model Input Feature: cleaned_review_text strictly
    if FEATURE_COL not in data.columns:
        raise KeyError(f"Required input feature column '{FEATURE_COL}' not found in DataFrame.")

    # Validate that cleaned_review_text is non-empty string
    data[FEATURE_COL] = data[FEATURE_COL].fillna("").astype(str)
    empty_mask = data[FEATURE_COL].str.strip() == ""
    empty_count = int(empty_mask.sum())
    if empty_count > 0:
        logger.warning("Dropping %d records with empty '%s'.", empty_count, FEATURE_COL)
        data = data[~empty_mask].copy()

    # 2. Derive Target Label Exclusively from star_rating
    ratings = pd.to_numeric(data["star_rating"], errors="coerce")
    if ratings.isnull().any():
        raise ValueError("Encountered null or invalid values in 'star_rating'.")

    if experiment_type == "binary":
        # Exclude 3-star (neutral) reviews exclusively from Experiment A
        # Positive: 4-5 stars, Negative: 1-2 stars
        data = data[ratings != NEUTRAL_RATING_VAL].copy()
        ratings_binary = pd.to_numeric(data["star_rating"], errors="coerce")
        data["target"] = np.where(
            ratings_binary >= POSITIVE_RATING_MIN,
            "positive",
            "negative",
        )
        valid_classes = BINARY_CLASSES
    elif experiment_type == "three_class":
        # Include all 3 classes: Positive (4-5), Neutral (3), Negative (1-2)
        def map_three_class(rating: float) -> str:
            if rating >= POSITIVE_RATING_MIN:
                return "positive"
            elif rating == NEUTRAL_RATING_VAL:
                return "neutral"
            return "negative"

        data["target"] = ratings.apply(map_three_class)
        valid_classes = THREE_CLASSES
    else:
        raise ValueError(f"Unknown experiment_type '{experiment_type}'. Choose 'binary' or 'three_class'.")

    # 3. Ensure target classes are valid
    data = data[data["target"].isin(valid_classes)].copy()

    # 4. Strict Column Isolation: retain only feature column, target, and slice metadata
    retained_cols = [FEATURE_COL, "target"]
    for slice_col in ["is_verified_purchase", "review_word_count"]:
        if slice_col in data.columns:
            retained_cols.append(slice_col)

    isolated_data = data[retained_cols].copy()

    logger.info(
        "Experiment '%s' prepared with %d samples across classes: %s. Feature: '%s' only.",
        experiment_type,
        len(isolated_data),
        dict(isolated_data["target"].value_counts()),
        FEATURE_COL,
    )
    return isolated_data
