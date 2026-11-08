"""Feature engineering module extracting temporal, lexical, and weak-supervision sentiment attributes."""

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.pipeline.config import (
    NEGATIVE_RATING_THRESHOLD,
    NEUTRAL_RATING_VALUE,
    POSITIVE_RATING_THRESHOLD,
)

logger = logging.getLogger(__name__)


def map_rating_to_category(star_rating: float) -> str:
    """Map star rating to weak-supervision proxy label.
    
    Weak-Supervision Rules:
    - 4.0 - 5.0 stars -> 'positive'
    - 3.0 stars       -> 'neutral'
    - 1.0 - 2.0 stars -> 'negative'
    
    IMPORTANT NOTE ON WEAK SUPERVISION:
    These categories represent rating-derived heuristic proxy labels. They reflect the
    customer's overall numerical score and NOT human-annotated ground truth text sentiment.
    In some cases, customer ratings and text tone diverge (e.g., giving 5 stars for sarcasm,
    or 1 star for delivery issues while praising the product itself).
    """
    try:
        val = float(star_rating)
    except (ValueError, TypeError):
        return "neutral"

    if val >= POSITIVE_RATING_THRESHOLD:
        return "positive"
    elif val == NEUTRAL_RATING_VALUE:
        return "neutral"
    elif val <= NEGATIVE_RATING_THRESHOLD:
        return "negative"
    else:
        # Fallback for ratings like 2.5 or 3.5
        return "positive" if val > NEUTRAL_RATING_VALUE else "negative"


def engineer_review_features(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich cleaned review data with lexical, temporal, and proxy sentiment features.
    
    Engineered Features:
    - review_text_length: Number of characters in the original review.
    - review_word_count: Number of words in the cleaned review text.
    - title_length: Number of characters in the original review title.
    - review_year: Year extracted from the review date.
    - review_month: Month extracted from the review date (1 - 12).
    - review_quarter: Quarter extracted from the review date (1 - 4).
    - is_verified_purchase: Boolean representation of verified purchase status.
    - rating_category: Weak-supervision sentiment category ('positive', 'neutral', 'negative').
    """
    logger.info("Extracting features on %d reviews...", len(df))
    out_df = df.copy()

    # 1. Lexical length features
    raw_text = out_df["review_text"].fillna("").astype(str)
    cleaned_text = (
        out_df["cleaned_review_text"].fillna("").astype(str)
        if "cleaned_review_text" in out_df.columns
        else raw_text
    )
    raw_title = out_df["review_title"].fillna("").astype(str)

    out_df["review_text_length"] = raw_text.str.len()
    out_df["review_word_count"] = cleaned_text.apply(lambda s: len(s.split()) if s else 0)
    out_df["title_length"] = raw_title.str.len()

    # 2. Temporal features
    dt_series = pd.to_datetime(out_df["review_date"], errors="coerce")
    out_df["review_year"] = dt_series.dt.year.fillna(0).astype(int)
    out_df["review_month"] = dt_series.dt.month.fillna(0).astype(int)
    out_df["review_quarter"] = dt_series.dt.quarter.fillna(0).astype(int)

    # 3. Verified purchase boolean
    out_df["is_verified_purchase"] = (
        out_df["verified_purchase"].astype(str).str.strip().str.lower().isin(["true", "1"])
    )

    # 4. Weak-supervision sentiment proxy labels
    out_df["rating_category"] = out_df["star_rating"].apply(map_rating_to_category)

    logger.info("Feature engineering complete. %d columns produced.", len(out_df.columns))
    return out_df

