"""Duplicate detection module distinguishing exact from contextual potential duplicates."""

import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)


def detect_review_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze reviews for exact duplicates and contextual potential duplicates without dropping them.
    
    Levels of Duplicate Analysis:
    1. Exact Duplicates: Every single column value is identical across rows.
    2. Event Duplicates: Same product_id, user_id, and review_timestamp.
    3. Content Duplicates: Same product_id and identical review text (may be legitimate repeated sentiment).
    """
    total_reviews = len(df)
    logger.info("Running duplicate detection on %d reviews...", total_reviews)

    # 1. Exact duplicates across all columns
    exact_mask = df.duplicated(keep=False)
    exact_count = int(exact_mask.sum())
    exact_samples = df[exact_mask].head(5).to_dict(orient="records") if exact_count > 0 else []

    # 2. Potential event duplicates by composite business key
    key_subset = [c for c in ["product_id", "user_id", "review_timestamp"] if c in df.columns]
    if len(key_subset) == 3:
        key_mask = df.duplicated(subset=key_subset, keep=False)
        key_count = int(key_mask.sum())
        key_samples = df[key_mask].head(5).to_dict(orient="records") if key_count > 0 else []
    else:
        key_count = 0
        key_samples = []

    # 3. Content duplicates on same product with identical text
    text_col = "cleaned_review_text" if "cleaned_review_text" in df.columns else "review_text"
    content_subset = ["product_id", text_col] if "product_id" in df.columns and text_col in df.columns else []
    if content_subset:
        content_mask = df.duplicated(subset=content_subset, keep=False)
        content_count = int(content_mask.sum())
        sample_cols = [c for c in ["product_id", "star_rating", text_col] if c in df.columns]
        content_samples = (
            df[content_mask][sample_cols].head(5).to_dict(orient="records")
            if content_count > 0
            else []
        )
    else:
        content_count = 0
        content_samples = []

    logger.info(
        "Duplicate detection results: %d exact duplicates, %d key duplicates, %d content duplicates.",
        exact_count,
        key_count,
        content_count,
    )

    return {
        "dataset": "reviews",
        "total_reviews": total_reviews,
        "exact_duplicates": {
            "count": exact_count,
            "samples": exact_samples,
        },
        "event_key_duplicates": {
            "fields": key_subset,
            "count": key_count,
            "samples": key_samples,
        },
        "content_duplicates": {
            "fields": content_subset,
            "count": content_count,
            "note": "Common short phrases (e.g. 'Works great!') across different users are legitimate reviews.",
            "samples": content_samples,
        },
    }


def detect_product_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze products for exact row duplicates and primary key collisions."""
    total_products = len(df)
    exact_count = int(df.duplicated(keep=False).sum())
    id_dupe_count = int(df.duplicated(subset=["product_id"], keep=False).sum()) if "product_id" in df.columns else 0

    return {
        "dataset": "products",
        "total_products": total_products,
        "exact_duplicates_count": exact_count,
        "product_id_duplicates_count": id_dupe_count,
    }


def run_duplicate_audit(reviews_df: pd.DataFrame, products_df: pd.DataFrame) -> Dict[str, Any]:
    """Execute complete duplicate detection audit."""
    rev_dupes = detect_review_duplicates(reviews_df)
    prod_dupes = detect_product_duplicates(products_df)

    return {
        "reviews_duplicates": rev_dupes,
        "products_duplicates": prod_dupes,
    }
